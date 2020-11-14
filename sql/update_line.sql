


update layer1_agv.io_state set io_status_id = {io_status_id},last_updated_user = 'GuoZi-SL',last_updated_timestamp = now()
where io_id = {io_id} returning io_id;
