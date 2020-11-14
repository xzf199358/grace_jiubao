select device_config.id,device_config.ip_address,device_config.port,device_config.device_name,
       device_config.device_id,device_config.device_type_id,device_config.do_cart_id,
       device_config.do_inter_id,device_config.di_inter_id,device_config.di_cart_id,device_config.repertory_io_id,
       device_config.query_ip,device_config.query_port
from layer1_agv.device_config
where device_config.device_id is not null and device_config.ip_address is not null and device_config.port is not null ;
