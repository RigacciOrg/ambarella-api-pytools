# Examples of messages received from the SJCAM SJ8 Pro camera
# in response of specific command messages.
#
# See:
# https://www.rigacci.org/wiki/doku.php/doc/appunti/hardware/sjcam-8pro-ambarella-wifi-api

socket_send(make_msg(msg_id=AMBA_START_SESSION))
Received: '{"rval":0,"msg_id":257,"param":2}'

socket_send(make_msg(msg_id=AMBA_GET_DEVICEINFO))
Received: '{"rval":0,"msg_id":11,"brand":"SJCAM","model":"SJ8PRO_TAIWAN","chip":"A12","app_type":"Connected","fw_ver":"local","api_ver":"4.1.0","media_folder":"/tmp/SD0/DCIM","event_folder":"/tmp/SD0/EVENT","http":"Disable","auth":"off","naming_rule":[{"type":"video","main_section":[0,6],"sensor_section":[6,1],"stream_section":[7,1]},{"type":"photo","main_section":[0,6],"offset_section":[6,2]}],"firmwareVersion":"V1.3.2"}'

socket_send(make_msg(msg_id=AMBA_GET_ALL_CURRENT_SETTINGS))
Received: '{"rval":0,"msg_id":3,"param":[{"Resolution":"1440 (2560x1440) 60FPS"},{"Power-On Record":"Off"},{"Video Lapse Resolution":"4K (3840x2160)"},{"Video Lapse":"1 Second"},{"Slow Motion":"-2X"},{"Image Size":"12MP 4000x3000 4:3"},{"Photo ISO":"Auto"},{"Shutter Speed":"Auto"},{"Photo Sharpness":"Standard"},{"Image Size":"12MP 4000x3000 4:3"},{"Photo Lapse Interval":"3 Seconds"},{"Photo Sharpness":"Standard"},{"Time photo ISO":"Auto"},{"Time photo shutter":"Auto"},{"Image Size":"12MP 4000x3000 4:3"},{"Burst Mode":"3 photos"},{"Burst ISO":"Auto"},{"Video_photo Resolution":"1080(1920x1080) 30FPS"},{"Photo Interval":"5 Seconds"},{"Resolution":"1440 (2560x1440) 60FPS"},{"EV":"+0.0"},{"White Balance":"Auto"},{"Color Profile":"SJCAM - Vivid"},{"Metering Mode":"Center"},{"Gyro Stabilizer":"On"},{"Encoding":"H.264"},{"Volume":"8"},{"Sharpness":"Standard"},{"Distortion Correction":"On"},{"Loop Recording":"Off"},{"File Size":"5 Minutes"},{"Video Quality":"Standard"},{"ISO":"MAX 6400"},{"Audio":"On"},{"Time Stamp":"Off"},{"EV":"+0.0"},{"White Balance":"Auto"},{"Color Profile":"SJCAM - Vivid"},{"Metering Mode":"Center"},{"Time Stamp":"Off"},{"Distortion Correction":"On"},{"RAW":"Off"},{"Photo Quality":"Standard"},{"Language":"en"},{"Format":"Cancel"},{"Auto Power Off":"3 Minutes"},{"LCD Off Time":"30 Seconds"},{"Front Display":"Off"},{"Indicator lights":"Off"},{"Keypad Tone":"On"},{"Rotate":"Off"},{"External microphone":"Off"},{"Gimbal Control":"Off"},{"Frequency":"50 Hz"},{"Default Setting":"Cancel"},{"Display ISO":"On"},{"User Interface":"Classic"}]}'

socket_send(make_msg(msg_id=AMBA_GET_SETTING, msg_type='camera_mode'))
Received: '{"rval":0,"msg_id":1,"type":"camera_mode","param":"normal_record"}'
Received: '{"rval":0,"msg_id":1,"type":"camera_mode","param":"timelapse_video"}'
Received: '{"rval":0,"msg_id":1,"type":"camera_mode","param":"slow_video"}'
Received: '{"rval":0,"msg_id":1,"type":"camera_mode","param":"normal_capture"}'
Received: '{"rval":0,"msg_id":1,"type":"camera_mode","param":"timelapse_photo"}'
Received: '{"rval":0,"msg_id":1,"type":"camera_mode","param":"burst_capture"}'
Received: '{"rval":0,"msg_id":1,"type":"camera_mode","param":"car_mode"}'

socket_send(make_msg(msg_id=AMBA_GET_BATTERY_LEVEL))
Received: '{"rval":0,"msg_id":13,"type":"adapter","param":100}'
Received: '{"rval":0,"msg_id":13,"type":"battery","param":25}'

socket_send(make_msg(msg_id=AMBA_GET_SPACE, msg_type='total'))
Received: '{"rval":0,"msg_id":5,"param":61765632}'

socket_send(make_msg(msg_id=AMBA_GET_SPACE, msg_type='free'))
Received: '{"rval":0,"msg_id":5,"param":51504768}'

socket_send(make_msg(msg_id=AMBA_GET_SINGLE_SETTING_OPTIONS, param='Front Display'))
Received '{"rval":0,"msg_id":9,"permission":"settable","param":"Front Display","options":["Off","On"]}'

socket_send(make_msg(msg_id=AMBA_GET_SINGLE_SETTING_OPTIONS, param='LCD Off Time'))
Received: '{"rval":0,"msg_id":9,"permission":"settable","param":"LCD Off Time","options":["Off","30 Seconds","1 Minute","3 Minutes","5 Minutes"]}'

socket_send(make_msg(msg_id=AMBA_GET_RECORD_TIME))
Received: '{"rval":0,"msg_id":515,"param":32}'

socket_send(make_msg(msg_id=AMBA_SET_SETTING, msg_type='camera_clock', param=date_time))
Received: '{"rval":0,"msg_id":2,"type":"camera_clock"}'

socket_send(make_msg(msg_id=AMBA_SET_SETTING, msg_type=key, param=val))
Received: '{"rval":0,"msg_id":2,"type":"Front Display"}'

socket_send(make_msg(msg_id=AMBA_SET_SETTING, msg_type='camera_mode', param='normal_record'))
Received: '{"rval":0,"msg_id":2,"type":"camera_mode"}{"msg_id":7,"type":"normal_record"}'

socket_send(make_msg(msg_id=AMBA_RECORD_START))
Received: '{"rval":0,"msg_id":513}{"msg_id":7,"type":"start_normal_record"}'
Received: '{"rval":0,"msg_id":513}{"msg_id":7,"type":"start_normal_capture"}'
Received: '{"rval":-1,"msg_id":513}'   # Already recording

socket_send(make_msg(msg_id=AMBA_STOP_SESSION))
Received: '{"rval":0,"msg_id":258}'

socket_send(make_msg(msg_id=AMBA_SET_SETTING, msg_type='Resolution', param='1080(1920x1080) 30FPS'))
Received: '{"rval":0,"msg_id":2,"type":"camera_mode"}'

# Other messages captured sniffing the SJCAM Zone app,
# not jet reverse engineered:
# {"param":"on","msg_id":2,"type":"save_low_resolution_clip","token":1}
# {"param":"rtsp","msg_id":2,"type":"stream_out_type","token":1}
