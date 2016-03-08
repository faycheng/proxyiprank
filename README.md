# proxyiprank

---
使用python实现的一个简单的代理ip检测库
更多内容可以查看proxyip_spider分支

## 特性
>* 能够对指定的代理IP进行可用性检测
>* 允许自定义用于代理IP检测的URL，代理IP检测次数，日志输出路径，检测超时以及简单的IP淘汰百分比
>* 可输出JSON形式的检测记录和可用IP列表
>* 对所有待检测IP都会进行信息统计，如平均检测时间，通过率，最近检测时，每次检测使用的时间等

## 使用示例
```
# 被检测的ip，必须是dict，key为ip地址，value为port（string）
proxyip_dict = {}
proxyip_dict['10.0.0.2'] = '8090'
proxyip_dict['10.0.0.3'] = '8090'

checking_test = ProxyIPRank(proxyip_dict, 5000)
checking_test.set_check_times(10)   # 设置每个IP检测10次
checking_test.set_availability_percent(0.9) # 设置IP检测成功次数/IP检测总次数大于0.9才视作可用IP
checking_test.set_target_url("http://www.chengxuyuanfei.com/")  # 使用指定网址www.chengxuyuanfei.com检测IP可用性
checking_test.set_chect_timeout(10) #设置每次IP检测超时等待的时间
checking_test.start_check_proxyips()    # 开始检查
checking_test.save_to_disk()    # 输出检测结果，默认为当前文件夹下
```

## 输出结果示例
proxyiprank.record.json
```
{"62.23.54.195:8080": {"check_record": [10, 10, 10, 10, 13.926981925964355, 15.81203007698059, 10, 10, 16.40651798248291, 14.27680516242981], "lastest_check_time": "2015.09.08-06:24:42", "availability_rate": 0.0, "avg_time": 12.042233514785767, "disperse_rate": 2.585115827786032},  "118.141.72.148:80": {"check_record": [10, 10, 10, 10, 10, 10, 10, 10, 10, 10], "avg_time": 10.0, "disperse_rate": 0.0, "availability_rate": 0.0, "lastest_check_time": "2015.09.09-11:28:11"}, "117.175.9.108:8123": {"disperse_rate": 0.0, "check_record": [10, 10, 10, 10, 10, 10, 10, 10, 10, 10], "availability_rate": 0.0, "avg_time": 10.0, "lastest_check_time": "2015.09.09-12:00:44"}, "124.193.23.158:3128": {"check_record": [10, 10, 10, 10, 10, 10, 10, 10, 10, 10], "lastest_check_time": "2015.09.09-06:33:09", "availability_rate": 0.0, "avg_time": 10.0, "disperse_rate": 0.0}, "103.4.254.6:80": {"check_record": [10, 10, 10, 10, 10, 10, 10, 10, 10, 10], "lastest_check_time": "2015.09.09-06:33:19", "availability_rate": 0.0, "avg_time": 10.0, "disperse_rate": 0.0}, "123.59.25.227:80": {"check_record": [10, 10, 10, 10, 10, 10, 10, 10, 10, 10], "lastest_check_time": "2015.09.09-08:10:44", "availability_rate": 0.0, "avg_time": 10.0, "disperse_rate": 0.0}, "139.227.198.127:8090": {"check_record": [10, 10, 10, 10, 10, 10, 10, 10, 10, 10], "lastest_check_time": "2015.09.08-06:24:38", "availability_rate": 0.0, "avg_time": 10.0, "disperse_rate": 0.0}, "139.227.177.54:8090": {"check_record": [10, 10, 10, 10, 10, 10, 10, 10, 10, 10], "lastest_check_time": "2015.09.07-20:30:05", "availability_rate": 0.0, "avg_time": 10.0, "disperse_rate": 0.0}, "218.95.82.145:9000": {"check_record": [10, 10, 10, 10, 10, 10, 10, 10, 10, 10], "lastest_check_time": "2015.09.08-18:20:48", "availability_rate": 0.0, "avg_time": 10.0, "disperse_rate": 0.0}, "113.245.210.11:80": {"disperse_rate": 0.0, "check_record": [10, 10, 10, 10, 10, 10, 10, 10, 10, 10], "availability_rate": 0.0, "avg_time": 10.0, "lastest_check_time": "2015.09.09-12:00:44"}, "202.106.169.142:80": {"check_record": [16.73299503326416, 10, 10, 9.230777978897095, 17.018294095993042, 10, 16.73547387123108, 8.764490127563477, 10, 17.56391215324402], "lastest_check_time": "2015.09.08-06:24:45", "availability_rate": 0.2, "avg_time": 12.604594326019287, "disperse_rate": 3.625577479508042}, "182.139.168.144:8090": {"check_record": [10, 10, 10, 10, 10, 10, 10, 10, 10, 10], "lastest_check_time": "2015.09.08-07:30:43", "availability_rate": 0.0, "avg_time": 10.0, "disperse_rate": 0.0}}
```

proxyiprank.availability.json
```
{
    "218.85.134.229:8899": {
        "disperse_rate": 0.8864789666386882, 
        "check_record": [
            0.22442412376403809, 
            0.24387097358703613, 
            0.22814702987670898, 
            0.2695150375366211, 
            0.26117420196533203, 
            3.215955972671509, 
            0.28928709030151367, 
            0.2760288715362549, 
            0.2933809757232666, 
            0.27181100845336914
        ], 
        "availability_rate": 1.0, 
        "avg_time": 0.5573595285415649, 
        "lastest_check_time": "2015.09.09-12:00:35"
    }, 
    "111.1.51.81:80": {
        "disperse_rate": 0.011265055823787012, 
        "check_record": [
            0.13179302215576172, 
            0.16999483108520508, 
            0.13759708404541016, 
            0.1326310634613037, 
            0.132066011428833, 
            0.14571499824523926, 
            0.13773584365844727, 
            0.1316080093383789, 
            0.13759517669677734, 
            0.13106513023376465
        ], 
        "availability_rate": 1.0, 
        "avg_time": 0.1387801170349121, 
        "lastest_check_time": "2015.09.09-12:00:35"
    }
}
```

