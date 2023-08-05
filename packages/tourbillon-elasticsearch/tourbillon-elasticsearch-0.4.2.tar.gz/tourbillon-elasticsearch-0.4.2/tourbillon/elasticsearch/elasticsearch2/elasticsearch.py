import logging
import urlparse

import requests
import trollius as asyncio
from trollius import From


logger = logging.getLogger(__name__)


@asyncio.coroutine
def get_es_cluster_stats(agent):
    yield From(agent.run_event.wait())
    logger.debug('starting get_elasticsearch_stats')
    config = agent.config['elasticsearch']
    logger.debug('get_elasticsearch_stats config retrieved')
    db_config = config['database']
    yield From(agent.async_create_database(**db_config))
    base_url = config['base_url']
    loop = asyncio.get_event_loop()
    while agent.run_event.is_set():
        logger.debug('in while loop')
        try:
            yield From(asyncio.sleep(config['frequency']))
            points = [{
                'measurement': 'es_cluster_stats',
                'tags': {
                    'hostname': config['host'],
                },
                'fields': {
                }
            }]
            cluster_stats_url = urlparse.urljoin(base_url,
                                                 '_cluster/stats')
            res = yield From(loop.run_in_executor(
                None, requests.get, cluster_stats_url))
            fields = points[0]['fields']
            if res.status_code == 200:
                info = res.json()
                points[0]['tags']['cluster_name'] = info['cluster_name']
                fields['status'] = info['status']
                fields['total_indices'] =\
                    info['indices']['count']
                fields['total_shards'] =\
                    info['indices']['shards']['total']
                fields['primaries_shards'] =\
                    info['indices']['shards']['primaries']
                fields['replication_shards'] =\
                    info['indices']['shards']['replication']
                fields['total_docs'] =\
                    info['indices']['docs']['count']
                fields['total_deleted_docs'] =\
                    info['indices']['docs']['deleted']
                fields['store_size_in_bytes'] =\
                    info['indices']['store']['size_in_bytes']
                fields['store_throttle_time_in_millis'] =\
                    info['indices']['store']['throttle_time_in_millis']
                fields['fielddata_memory_size_in_bytes'] =\
                    info['indices']['fielddata']['memory_size_in_bytes']
                fields['fielddata_evictions'] =\
                    info['indices']['fielddata']['evictions']
                fields['filter_cache_memory_size_in_bytes'] =\
                    info['indices']['filter_cache']['memory_size_in_bytes']
                fields['filter_cache_evictions'] =\
                    info['indices']['filter_cache']['evictions']
                fields['id_cache_memory_size_in_bytes'] =\
                    info['indices']['id_cache']['memory_size_in_bytes']
                fields['completion_size_in_bytes'] =\
                    info['indices']['completion']['size_in_bytes']
                fields['segments_count'] =\
                    info['indices']['segments']['count']
                fields['segments_count'] =\
                    info['indices']['segments']['count']
                fields['percolate_total'] =\
                    info['indices']['percolate']['total']
                fields['percolate_time_in_millis'] =\
                    info['indices']['percolate']['time_in_millis']
                fields['percolate_memory_size_in_bytes'] =\
                    info['indices']['percolate']['memory_size_in_bytes']
                fields['process_cpu_percent'] =\
                    info['nodes']['process']['cpu']['percent']
                fields['process_open_file_descriptors_min'] =\
                    info['nodes']['process']['open_file_descriptors']['min']
                fields['process_open_file_descriptors_max'] =\
                    info['nodes']['process']['open_file_descriptors']['max']
                fields['process_open_file_descriptors_avg'] =\
                    info['nodes']['process']['open_file_descriptors']['avg']
                fields['jvm_mem_heap_used_in_bytes'] =\
                    info['nodes']['jvm']['mem']['heap_used_in_bytes']
                fields['jvm_mem_heap_max_in_bytes'] =\
                    info['nodes']['jvm']['mem']['heap_max_in_bytes']
                fields['jvm_threads'] =\
                    info['nodes']['jvm']['threads']
                fields['fs_total_in_bytes'] =\
                    info['nodes']['fs']['total_in_bytes']
                fields['fs_free_in_bytes'] =\
                    info['nodes']['fs']['free_in_bytes']
                fields['fs_available_in_bytes'] =\
                    info['nodes']['fs']['available_in_bytes']
                fields['fs_disk_reads'] =\
                    info['nodes']['fs']['disk_reads']
                fields['fs_disk_writes'] =\
                    info['nodes']['fs']['disk_writes']
                fields['fs_disk_io_op'] =\
                    info['nodes']['fs']['disk_io_op']
                fields['fs_disk_read_size_in_bytes'] =\
                    info['nodes']['fs']['disk_read_size_in_bytes']
                fields['fs_disk_write_size_in_bytes'] =\
                    info['nodes']['fs']['disk_write_size_in_bytes']
                fields['fs_disk_io_size_in_bytes'] =\
                    info['nodes']['fs']['disk_io_size_in_bytes']
                fields['fs_disk_queue'] =\
                    info['nodes']['fs']['disk_queue']
                fields['disk_service_time'] =\
                    info['nodes']['fs']['disk_service_time']
                logger.debug('es data: {}'.format(points))
                yield From(agent.async_push(points, db_config['name']))
            else:
                logger.warning('cannot get nginx stats: status={}'
                               .format(res.status_code))
        except:
            logger.exception('cannot get nginx stats')
    logger.info('get_elasticsearch_stats terminated')


@asyncio.coroutine
def get_es_nodes_stats(agent):
    yield From(agent.run_event.wait())
    logger.debug('starting get_es_nodes_stats')
    config = agent.config['elasticsearch']
    logger.debug('get_es_nodes_stats config retrieved')
    db_config = config['database']
    yield From(agent.async_create_database(**db_config))
    base_url = config['base_url']
    loop = asyncio.get_event_loop()
    while agent.run_event.is_set():
        logger.debug('in while loop')
        try:
            yield From(asyncio.sleep(config['frequency']))
            points = []
            nodes_stats_url = urlparse.urljoin(base_url,
                                               '_nodes/stats')
            res = yield From(loop.run_in_executor(
                None, requests.get, nodes_stats_url))

            if res.status_code == 200:
                info = res.json()
                cluster_name = info['cluster_name']
                for node in info['nodes'].values():
                    point = {
                        'measurement': 'es_nodes_stats',
                        'tags': {
                            'hostname': node['host'],
                            'cluster_name': cluster_name,
                            'name': node['name']
                        },
                        'fields': {
                        }
                    }
                    fields = point['fields']
                    fields['indices_docs_count'] =\
                        node['indices']['docs']['count']
                    fields['indices_docs_deleted'] =\
                        node['indices']['docs']['deleted']
                    fields['indices_store_size_in_bytes'] =\
                        node['indices']['store']['size_in_bytes']
                    fields['indices_store_throttle_time_in_millis'] =\
                        node['indices']['store']['throttle_time_in_millis']
                    fields['indices_indexing_index_total'] =\
                        node['indices']['indexing']['index_total']
                    fields['indices_indexing_index_time_in_millis'] =\
                        node['indices']['indexing']['index_time_in_millis']
                    fields['indices_indexing_index_current'] =\
                        node['indices']['indexing']['index_current']

                    fields['indices_indexing_delete_total'] =\
                        node['indices']['indexing']['delete_total']
                    fields['indices_indexing_delete_time_in_millis'] =\
                        node['indices']['indexing']['delete_time_in_millis']
                    fields['indices_indexing_delete_current'] =\
                        node['indices']['indexing']['delete_current']

                    fields['indices_get_total'] =\
                        node['indices']['get']['total']
                    fields['indices_get_time_in_millis'] =\
                        node['indices']['get']['time_in_millis']
                    fields['indices_get_exists_total'] =\
                        node['indices']['get']['exists_total']
                    fields['indices_get_exists_time_in_millis'] =\
                        node['indices']['get']['exists_time_in_millis']
                    fields['indices_get_missing_total'] =\
                        node['indices']['get']['missing_total']
                    fields['indices_get_missing_time_in_millis'] =\
                        node['indices']['get']['missing_time_in_millis']
                    fields['indices_get_current'] =\
                        node['indices']['get']['current']

                    fields['indices_search_open_contexts'] =\
                        node['indices']['search']['open_contexts']
                    fields['indices_search_query_total'] =\
                        node['indices']['search']['query_total']
                    fields['indices_search_query_time_in_millis'] =\
                        node['indices']['search']['query_time_in_millis']
                    fields['indices_search_query_current'] =\
                        node['indices']['search']['query_current']
                    fields['indices_search_fetch_total'] =\
                        node['indices']['search']['fetch_total']
                    fields['indices_search_fetch_time_in_millis'] =\
                        node['indices']['search']['fetch_time_in_millis']
                    fields['indices_search_fetch_current'] =\
                        node['indices']['search']['fetch_current']

                    fields['indices_merges_current'] =\
                        node['indices']['merges']['current']
                    fields['indices_merges_current_docs'] =\
                        node['indices']['merges']['current_docs']
                    fields['indices_merges_current_size_in_bytes'] =\
                        node['indices']['merges']['current_size_in_bytes']
                    fields['indices_merges_total'] =\
                        node['indices']['merges']['total']
                    fields['indices_merges_total_time_in_millis'] =\
                        node['indices']['merges']['total_time_in_millis']
                    fields['indices_merges_total_docs'] =\
                        node['indices']['merges']['total_docs']
                    fields['indices_merges_total_size_in_bytes'] =\
                        node['indices']['merges']['total_size_in_bytes']

                    fields['indices_refresh_total'] =\
                        node['indices']['refresh']['total']
                    fields['indices_refresh_total_time_in_millis'] =\
                        node['indices']['refresh']['total_time_in_millis']

                    fields['indices_flush_total'] =\
                        node['indices']['flush']['total']
                    fields['indices_flush_total_time_in_millis'] =\
                        node['indices']['flush']['total_time_in_millis']

                    fields['indices_warmer_current'] =\
                        node['indices']['warmer']['current']
                    fields['indices_warmer_total'] =\
                        node['indices']['warmer']['total']
                    fields['indices_warmer_total_time_in_millis'] =\
                        node['indices']['warmer']['total_time_in_millis']

                    fields['indices_filter_cache_memory_size_in_bytes'] =\
                        node['indices']['filter_cache']['memory_size_in_bytes']
                    fields['indices_filter_cache_evictions'] =\
                        node['indices']['filter_cache']['evictions']

                    fields['indices_id_cache_memory_size_in_bytes'] =\
                        node['indices']['id_cache']['memory_size_in_bytes']

                    fields['indices_fielddata_memory_size_in_bytes'] =\
                        node['indices']['fielddata']['memory_size_in_bytes']
                    fields['indices_fielddata_evictions'] =\
                        node['indices']['fielddata']['evictions']

                    fields['indices_percolate_total'] =\
                        node['indices']['percolate']['total']
                    fields['indices_percolate_time_in_millis'] =\
                        node['indices']['percolate']['time_in_millis']
                    fields['indices_percolate_current'] =\
                        node['indices']['percolate']['current']
                    fields['indices_percolate_memory_size_in_bytes'] =\
                        node['indices']['percolate']['memory_size_in_bytes']
                    fields['indices_percolate_queries'] =\
                        node['indices']['percolate']['queries']

                    fields['indices_completion_size_in_bytes'] =\
                        node['indices']['completion']['size_in_bytes']

                    segments = node['indices']['segments']
                    fields['indices_segments_count'] =\
                        segments['count']
                    fields['indices_segments_memory_in_bytes'] =\
                        segments['memory_in_bytes']
                    fields['indices_segments_index_writer_memory_in_bytes'] =\
                        segments['index_writer_memory_in_bytes']
                    fields['indices_segments_version_map_memory_in_bytes'] =\
                        segments['version_map_memory_in_bytes']

                    fields['indices_translog_operations'] =\
                        node['indices']['translog']['operations']
                    fields['indices_translog_size_in_bytes'] =\
                        node['indices']['translog']['size_in_bytes']

                    fields['indices_suggest_total'] =\
                        node['indices']['suggest']['total']
                    fields['indices_suggest_time_in_millis'] =\
                        node['indices']['suggest']['time_in_millis']
                    fields['indices_suggest_current'] =\
                        node['indices']['suggest']['current']

                    fields['process_cpu_percent'] =\
                        node['process']['cpu']['percent']
                    fields['process_cpu_sys_in_millis'] =\
                        node['process']['cpu']['sys_in_millis']
                    fields['process_cpu_user_in_millis'] =\
                        node['process']['cpu']['user_in_millis']
                    fields['process_cpu_total_in_millis'] =\
                        node['process']['cpu']['total_in_millis']

                    fields['process_mem_resident_in_bytes'] =\
                        node['process']['mem']['resident_in_bytes']
                    fields['process_mem_share_in_bytes'] =\
                        node['process']['mem']['share_in_bytes']
                    fields['process_mem_total_virtual_in_bytes'] =\
                        node['process']['mem']['total_virtual_in_bytes']

                    fields['jvm_mem_heap_used_in_bytes'] =\
                        node['jvm']['mem']['heap_used_in_bytes']
                    fields['jvm_mem_heap_used_percent'] =\
                        node['jvm']['mem']['heap_used_percent']
                    fields['jvm_mem_heap_committed_in_bytes'] =\
                        node['jvm']['mem']['heap_committed_in_bytes']
                    fields['jvm_mem_heap_max_in_bytes'] =\
                        node['jvm']['mem']['heap_max_in_bytes']
                    fields['jvm_mem_non_heap_used_in_bytes'] =\
                        node['jvm']['mem']['non_heap_used_in_bytes']
                    fields['jvm_mem_non_heap_committed_in_bytes'] =\
                        node['jvm']['mem']['non_heap_committed_in_bytes']

                    young_pool = node['jvm']['mem']['pools']['young']
                    fields['jvm_mem_pools_young_used_in_bytes'] =\
                        young_pool['used_in_bytes']
                    fields['jvm_mem_pools_young_max_in_bytes'] =\
                        young_pool['max_in_bytes']
                    fields['jvm_mem_pools_young_peak_used_in_bytes'] =\
                        young_pool['peak_used_in_bytes']
                    fields['jvm_mem_pools_young_peak_max_in_bytes'] =\
                        young_pool['peak_max_in_bytes']

                    survivor_pool = node['jvm']['mem']['pools']['survivor']
                    fields['jvm_mem_pools_survivor_used_in_bytes'] =\
                        survivor_pool['used_in_bytes']
                    fields['jvm_mem_pools_survivor_max_in_bytes'] =\
                        survivor_pool['max_in_bytes']
                    fields['jvm_mem_pools_survivor_peak_used_in_bytes'] =\
                        survivor_pool['peak_used_in_bytes']
                    fields['jvm_mem_pools_survivor_peak_max_in_bytes'] =\
                        survivor_pool['peak_max_in_bytes']

                    old_pool = node['jvm']['mem']['pools']['old']
                    fields['jvm_mem_pools_old_used_in_bytes'] =\
                        old_pool['used_in_bytes']
                    fields['jvm_mem_pools_old_max_in_bytes'] =\
                        old_pool['max_in_bytes']
                    fields['jvm_mem_pools_old_peak_used_in_bytes'] =\
                        old_pool['peak_used_in_bytes']
                    fields['jvm_mem_pools_old_peak_max_in_bytes'] =\
                        old_pool['peak_max_in_bytes']

                    fields['jvm_threads_count'] =\
                        node['jvm']['threads']['count']
                    fields['jvm_threads_peak_count'] =\
                        node['jvm']['threads']['peak_count']

                    gc_young_col = node['jvm']['gc']['collectors']['young']
                    fields['jvm_gc_col_young_collection_count'] =\
                        gc_young_col['collection_count']
                    fields['jvm_gc_col_young_collection_time_in_millis'] =\
                        gc_young_col['collection_time_in_millis']

                    gc_old_col = node['jvm']['gc']['collectors']['old']
                    fields['jvm_gc_col_old_collection_count'] =\
                        gc_old_col['collection_count']
                    fields['jvm_gc_col_old_collection_time_in_millis'] =\
                        gc_old_col['collection_time_in_millis']

                    dir_buf_pool = node['jvm']['buffer_pools']['direct']
                    fields['jvm_bufpool_direct_count'] =\
                        dir_buf_pool['count']
                    fields['jvm_bufpool_direct_used_in_bytes'] =\
                        dir_buf_pool['used_in_bytes']
                    fields['jvm_bufpool_direct_total_capacity_in_bytes'] =\
                        dir_buf_pool['total_capacity_in_bytes']

                    map_buf_pool = node['jvm']['buffer_pools']['mapped']
                    fields['jvm_bufpool_mapped_count'] =\
                        map_buf_pool['count']
                    fields['jvm_bufpool_mapped_used_in_bytes'] =\
                        map_buf_pool['used_in_bytes']
                    fields['jvm_bufpool_mapped_total_capacity_in_bytes'] =\
                        map_buf_pool['total_capacity_in_bytes']

                    for pool in ('generic', 'index', 'snapshot_data', 'bench',
                                 'get', 'snapshot', 'merge', 'suggest', 'bulk',
                                 'optimize', 'warmer', 'flush', 'search',
                                 'percolate', 'management', 'refresh'):
                        for k, v in node['thread_pool'][pool].items():
                            field_name = 'threadpool_{}_{}'.format(pool, k)
                            fields[field_name] = v

                    for k, v in node['network']['tcp'].items():
                        field_name = 'network_tcp_{}'.format(k)
                        fields[field_name] = v

                    for k, v in node['fs']['total'].items():
                        field_name = 'fs_total_{}'.format(k)
                        fields[field_name] = v

                    for metric_group in ('transport', 'http',
                                         'fielddata_breaker'):
                        for k, v in node[metric_group].items():
                            if metric_group == 'fielddata_breaker' and\
                                    k in ('maximum_size', 'estimated_size'):
                                continue
                            field_name = '{}_{}'.format(metric_group, k)
                            fields[field_name] = v

                    points.append(point)
                logger.debug('es data: {}'.format(points))
                yield From(agent.async_push(points, db_config['name']))
            else:
                logger.warning('cannot get nginx stats: status={}'
                               .format(res.status_code))
        except:
            logger.exception('cannot get nginx stats')
    logger.info('get_elasticsearch_stats terminated')
