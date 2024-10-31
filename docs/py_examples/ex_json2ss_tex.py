from noltaSympoPubTools.json2tex import json2ss_tex

json2ss_tex(
    data_json="data.json",
    ss_organizers_json="ss_organizers.json",
    output="ss_list.tex",
    session_name_prefix_cnt=1,
)
