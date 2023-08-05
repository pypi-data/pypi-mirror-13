import logging
import datetime

from optparse import make_option

from django import VERSION as dj_version

logger = logging.getLogger(__name__)


def get_index_name(type_obj, a_datetime):
    if type_obj["index"] and not type_obj["idx_alias"]:
        return type_obj["index"]
    if a_datetime is None:
        raise Exception("execute time shouldn't be None")
    return type_obj["idx_alias"] + "-" + a_datetime.strftime("%Y-%m-%d-%H-%M-%S-%f")


def populate_parse_stop_time(stop_time_in):
    if not stop_time_in:
        return None
    now = datetime.datetime.now()
    ymd_str = now.strftime("%Y-%m-%d")
    stop_time_str = ymd_str + " " + stop_time_in
    stop_time = datetime.datetime.strptime(stop_time_str, "%Y-%m-%d %H:%M")
    if stop_time < now:
        stop_time += datetime.timedelta(days=1)
    return stop_time

func_map = {
    "populate": {
        "args": {
            "doc_type": lambda x: x,
            "num_processes": lambda n: int(n),
            "limit": lambda n: int(n) if n else None,
            "stop_time": populate_parse_stop_time,
            "query_chunk_size": lambda n: int(n)
        }
    },
    "create": {
        "args": {
            "doc_type": lambda x: x
        }
    },
    "startover": {
        "args": {
            "doc_type": lambda x: x
        }
    },
    "reindex": {
        "args": {
            "doc_type": lambda x: x,
            "num_processes": lambda n: int(n),
            "limit": lambda n: int(n) if n else None,
            "stop_time": populate_parse_stop_time,
            "query_chunk_size": lambda n: int(n)
        }
    },
}


def get_cli_options(type_choices):
    return (
        make_option(
            "-t", "--doc-type",
            choices=type_choices.keys(),
            dest="doc_type",
        ),
        make_option(
            "-c", "--cmd",
            choices=func_map.keys(),
            dest="command",
        ),
        make_option(
            "-p", "--num-processes",
            dest="num_processes",
            default=5
        ),
        make_option(
            "-n", "--num-to-index",
            dest="limit",
            help="enter a number. Default is no limit",
        ),
        make_option(
            "-s", "--stop-time",
            dest="stop_time",
            help="enter a time in format %H:%M. If it's less than today's current time, it will be set for tomorrow at that time",
        ),
        make_option(
            "-k", "--query-chunk-size",
            dest="query_chunk_size",
            default=8000,
            help="can be adjusted for memory usage",
        ),
    )


def main(type_choices, es_obj, options):
    from functools import partial

    start_time = datetime.datetime.now()
    # try:
    command = options["command"]
    if command not in func_map.keys():
        raise Exception("invalid selection for --cmd, please use one of %s" % func_map.keys())
    doc_type = options["doc_type"]
    if not doc_type:
        raise Exception("doc type is required")

    func_args = func_map[command].get("args", {})
    func_args_vals = [arg_parse_func(options[arg_name]) for arg_name, arg_parse_func in func_args.iteritems()]

    type_func = partial(globals()[command], type_choices, es_obj, start_time)
    cmd_report = type_func(*func_args_vals)
    return cmd_report


def startover(type_choices, es_obj, begin_time, doc_type):
    logger.debug("starting over for type = %s" % doc_type)
    type_obj = type_choices[doc_type]

    idx_client = es_obj.indices
    index_name = get_index_name(type_obj, begin_time)
    logger.debug("removing mapping for index: %s" % index_name)
    if idx_client.exists_type(index=index_name, doc_type=doc_type):
        es_obj.indices.delete_mapping(index=index_name, doc_type=doc_type)

    if type_obj["post_startover_func"]:
        logger.debug("post startover func")
        type_obj["post_startover_func"]()

    cmd_report = create(type_choices, es_obj, begin_time, doc_type)

    return [{
        "name": "startover",
        "begin_time": str(begin_time),
        "doc_type": doc_type,
        "sub_commands": cmd_report,
    }]


def create(type_choices, es_obj, begin_time, doc_type):
    logger.debug("creating type = %s" % doc_type)
    type_obj = type_choices[doc_type]

    if not type_obj["mapping"]:
        logger.debug("no mapping defined for doc_type = %s.  Nothing to do here" % doc_type)
        return

    idx_client = es_obj.indices

    index_name = get_index_name(type_obj, begin_time)
    if not idx_client.exists(index=index_name):
        idx_client.create(index=index_name)

    if idx_client.exists_type(index=index_name, doc_type=doc_type):
        raise Exception("doc type already exists")

    idx_client.put_mapping(index=index_name, doc_type=doc_type, body=type_obj["mapping"])

    return [{
        "name": "create",
        "begin_time": str(begin_time),
        "doc_type": doc_type,
    }]


def get_indexes(es_obj, prefix=None, excluding=None):
    result = es_obj.indices.status()["indices"].keys()
    if not prefix and not excluding:
        return result
    if prefix:
        result = [idx_name for idx_name in result if idx_name.startswith(prefix)]
    if excluding and excluding in result:
        result.remove(excluding)
    return result


def reindex(type_choices, es_obj, begin_time, doc_type, num_processes, limit, stop_time, query_chunk_size):
    logger.debug("reindexing type = %s" % doc_type)

    type_obj = type_choices[doc_type]

    def reindex_single_doctype(single_type):
        subcmd_rpts1 = []
        subcmd_rpts1 += startover(type_choices, es_obj, begin_time, single_type)
        subcmd_rpts1 += populate(type_choices, es_obj, begin_time, single_type, num_processes, limit, stop_time, query_chunk_size)
        return [{
            "name": "reindex_single_doctype",
            "doc_type": single_type,
            "subcommands": subcmd_rpts1,
        }]

    subcmd_rpts = []
    if type_obj.get("combination"):
        for single_type in type_obj.get("combination"):
            subcmd_rpts += reindex_single_doctype(single_type)
    else:
        subcmd_rpts += reindex_single_doctype(doc_type)

    idx_alias_name = type_obj["idx_alias"]
    if idx_alias_name:
        index_name = get_index_name(type_obj, begin_time)
        logger.debug("idx_alias_name = %s" % idx_alias_name)
        if es_obj.indices.exists_alias(name=idx_alias_name):
            logger.debug("deleting alias: %s" % idx_alias_name)
            dela_res = es_obj.indices.delete_alias(index="_all", name=idx_alias_name)
            if not dela_res["acknowledged"]:
                raise Exception("failed to delete alias '%s'" % idx_alias_name)
        logger.debug("putting alias: %s" % idx_alias_name)
        es_obj.indices.put_alias(index=index_name, name=idx_alias_name)
        old_indices = get_indexes(es_obj, idx_alias_name, index_name)
        for old_idx in old_indices:
            logger.debug("deleting idx: %s" % old_idx)
            del_res = es_obj.indices.delete(index=old_idx)
            if not del_res["acknowledged"]:
                raise Exception("failed to delete old index '%s'" % old_idx)

    return [{
        "name": "reindex",
        "begin_time": str(begin_time),
        "doc_type": doc_type,
        "num_processes": num_processes,
        "limit": limit,
        "stop_time": str(stop_time),
        "subcommands": subcmd_rpts,
        "query_chunk_size": query_chunk_size,
    }]


def populate(type_choices, es_obj, begin_time, doc_type, num_processes, limit, stop_time, query_chunk_size):
    import multiprocessing
    from django import db

    if not doc_type:
        raise Exception("model type is required")

    logger.debug("populating type = %s" % doc_type)

    type_obj = type_choices[doc_type]

    index_name = get_index_name(type_obj, begin_time)

    start_time = datetime.datetime.now()

    if stop_time:
        logger.debug("A stop time was given of %s" % stop_time)

    def chunks(l, n):
        if n == 0:
            # yield empty generator
            return
            yield
        for i in xrange(0, len(l), n):
            yield l[i:i+n]

    row_ids = type_obj["query"].values_list("id", flat=True).order_by("id")
    if limit:
        row_ids = row_ids[:limit]

    total_count = row_ids.count()
    logger.debug("total to index %s" % total_count)

    num_done = multiprocessing.Value("i", 0)
    from ctypes import c_bool
    error_in_subprocess = multiprocessing.Value(c_bool, False)

    def es_index(model_type, ids, idx_func, num_done, query_chunk_size):
        try:
            index_start_time = datetime.datetime.now()
            if dj_version[0] == 1 and dj_version[1] <= 7:
                db.close_connection()
            # dataset_chunk_size = 8000
            chunked_row_ids = chunks(ids, query_chunk_size)

            def should_stop():
                if not stop_time:
                    return False
                now = datetime.datetime.now()
                return now > stop_time
            for chunk in chunked_row_ids:
                if should_stop():
                    logger.debug("stopped due to stop time reached")
                    break
                logger.debug("next chunk: len: %s, start: %s, end: %s" % (len(chunk), chunk[0], chunk[-1]))
                with db.transaction.atomic():
                    rows = model_type.objects.filter(id__in=chunk)
                    for row in rows:
                        if should_stop():
                            logger.debug("stopped due to stop time reached")
                            break
                        idx_func(row, index_name)
                        with num_done.get_lock():
                            num_done.value += 1
            index_finish_time = datetime.datetime.now()
            logger.debug("finished processing %s rows in %s" % (len(ids), index_finish_time - index_start_time))
        except Exception, e:
            with error_in_subprocess.get_lock():
                error_in_subprocess.value = True
            logger.exception(str(e))

    def reporting_func(num_done, stop_time):
        import time
        last_done = 0
        last_twenty = []
        while True:  # infinite - kill from outside
            time.sleep(3)
            num_done_now = num_done.value
            done_since_last = num_done.value - last_done
            last_twenty.append(done_since_last)
            if len(last_twenty) > 20:
                del last_twenty[0]
            stop_time_msg = " A stop time was given of %s it is now %s" % (stop_time, datetime.datetime.now()) if stop_time else ""
            logger.debug("%s done. %s since last. avg = %s.%s" % (num_done_now, done_since_last, float(sum(last_twenty)) / len(last_twenty), stop_time_msg))
            last_done = num_done_now

    reporting_process = multiprocessing.Process(target=reporting_func, args=(num_done, stop_time,))

    try:
        num_processes = num_processes if total_count >= num_processes else total_count
        logger.debug("num processes = %s" % num_processes)
        if num_processes > 1:
            import math
            process_chunk_size_division = float(total_count) / num_processes
            logger.debug("process_chunk_size_division = %s" % process_chunk_size_division)
            process_chunk_size = int(math.ceil(process_chunk_size_division))
            logger.debug("process chunk size = %s" % process_chunk_size)
            logger.debug("query chunk size = %s" % query_chunk_size)
            if query_chunk_size < process_chunk_size:
                logger.debug("will be chunking the query because the query chunk size is less than the process chunk size")
            else:
                logger.debug("no need to chunk the query because the query chunk size is greater than or equal to the process chunk size")

            process_chunks = list(chunks(row_ids, process_chunk_size))
            if num_processes != len(process_chunks):
                num_processes = len(process_chunks)
                logger.debug("num_processes adjusted = %s" % num_processes)

            index_processes = [multiprocessing.Process(target=es_index, args=(type_obj["model"], process_chunks[i], type_obj["idx_func"], num_done, query_chunk_size)) for i in range(num_processes)]
            reporting_process.start()
            for ip in index_processes:
                ip.start()
            for ip in index_processes:
                ip.join()
        else:
            reporting_process.start()
            es_index(type_obj["model"], row_ids, type_obj["idx_func"], num_done, query_chunk_size)

        if error_in_subprocess.value:
            raise Exception("There was at least one error during population")

    finally:
        logger.debug("terminating reporting process")
        reporting_process.terminate()

    db.close_connection()

    logger.debug("%s done" % num_done.value)

    finish_time = datetime.datetime.now()

    total_time = finish_time - start_time
    logger.debug("total time = %s" % (total_time))

    return [{
        "name": "populate",
        "begin_time": str(begin_time),
        "doc_type": doc_type,
        "num_processes": num_processes,
        "limit": limit,
        "stop_time": str(stop_time),
        "num_done": num_done.value,
        "total_time": str(total_time),
        "query_chunk_size": query_chunk_size,
    }]
