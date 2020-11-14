SELECT id, order_type_id, order_status_id, location_id, location_name, destination_location_id, destination_location_name,priority  FROM public.order_info where order_status_id = 0 order by id ;
