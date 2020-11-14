update public.order_info set order_no  = {order_no} ,order_status_id = {order_status_id}, last_updated_user = 'YSB', last_updated_timestamp = now()
where id = {id} returning id;
