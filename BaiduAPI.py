#coding : utf-8 
#author : zhangchi
#BaiduAPI.py 百度地图API部分接口的实现
import time
import urllib,urllib2,json
import hashlib
from exception import OfficialAPIError


class map:
    ak = ""
    coordtype = "wgs84ll"
    coord_type = 1
    sk = ""
    sn = ""

    def __init__(self, ak, sk, coordtype):
        '''
        initialization!
        :param ak: your ak
        :param sk: your sk
        :param coordtype: bd09ll（百度经纬度坐标）、bd09mc（百度米制坐标）、gcj02ll（国测局经纬度坐标）、wgs84ll（ GPS经纬度）
        '''
        self.ak = ak
        self.sk = sk
        self.coordtype = coordtype
        if coordtype == "bd09ll":
            self.coord_type = 3
        elif coordtype == "bd09mc":
            self.coord_type = 4
        elif coordtype == "gcj02ll":
            self.coord_type = 2
        elif coordtype == "wgs84ll":
            self.coord_type = 1
        else:
            coordtype == "wgs84ll"
            self.coord_type = 1

    def Get_LocationName(self, Latitude, Longitude):
        '''
        Get Location infomation
        :param Latitude: 纬度
        :param Longitude: 经度
        :return: dict include "status" (which is response status), "city", "address", "region"(which means a nearby building)
        如果想要其他信息可以自行修改
        '''
        queryStr = "/geocoder/v2/?coordtype="+self.coordtype+"&location=" + str(Latitude) + "," + str(Longitude) + "&output=json&pois=1&ak="+self.ak
        self.sn=self.Get_sn(queryStr)
        url = "http://api.map.baidu.com/geocoder/v2/?coordtype="+self.coordtype+"&location=" + str(Latitude) + "," + str(Longitude) + "&output=json&pois=1&ak="+self.ak+"&sn="+self.sn
        resp = urllib2.urlopen(url)
        reson = json.loads(resp.read())

        self._check_official_errors(reson)

        result = {
            "status": reson["status"],
            "city": reson["result"]["addressComponent"]["city"],
            "address": reson["result"]["formatted_address"],
            "region": reson["result"]["sematic_description"]
        }
        return result

    def Get_Nearby(self, query, Latitude, Longitude):
        """
        获取该坐标点附近相关信息
        :param query: 需要查询的关键字
        :param Latitude: 纬度
        :param Longitude: 经度
        :return: 数量和相关结果
        """
        queryStr = "/place/v2/search?coord_type="+str(self.coord_type)+"&output=json&query="+query+"&page_size=5&page_num=0&scope=2&location="+str(Latitude)+","+str(Longitude)+"&radius=2000&filter=sort_name:distance&ak="+self.ak
        self.sn = self.Get_sn(queryStr)
        url = "http://api.map.baidu.com/place/v2/search?coord_type="+str(self.coord_type)+"&output=json&query="+query+"&page_size=5&page_num=0&scope=2&location="+str(Latitude)+","+str(Longitude)+"&radius=2000&filter=sort_name:distance&ak="+self.ak+"&sn="+self.sn
        url = urllib.quote(url, safe="!*'();:@&=+$,/?%#[]")
        resp = urllib2.urlopen(url)
        reson = json.loads(resp.read())

        self._check_official_errors(reson)

        count = len(reson["results"])
        return count, reson["results"]

    def Geo_Coder(self, address, city):
        quertyStr = "/geocoder/v2/?output=json&address="+address+"&city="+city+"&ak="+self.ak
        self.sn = self.Get_sn(quertyStr)
        url = "http://api.map.baidu.com/geocoder/v2/?output=json&address="+address+"&city="+city+"&ak="+self.ak+"&sn="+self.sn
        url = urllib.quote(url, safe="!*'();:@&=+$,/?%#[]")

        resp = urllib2.urlopen(url)
        reson = json.loads(resp.read())

        self._check_official_errors(reson)

        return reson["result"]

    def Geo_Conv(self, coords, fromtype, totype):
        LocStr = ""
        for record in coords:
            if LocStr != "":
                LocStr = LocStr + ';'
            LocStr = LocStr + str(record["Latitude"])+","+str(record["Longitude"])
        quertyStr = "/geoconv/v1/?coords="+LocStr+"&from="+str(fromtype)+"&to="+str(totype)+"&ak="+self.ak
        self.sn = self.Get_sn(quertyStr)
        url = "http://api.map.baidu.com/geoconv/v1/?coords="+LocStr+"&from="+str(fromtype)+"&to="+str(totype)+"&ak="+self.ak+"&sn="+self.sn
        url = urllib.quote(url, safe="!*'();:@&=+$,/?%#[]")

        resp = urllib2.urlopen(url)
        reson = json.loads(resp.read())

        self._check_official_errors(reson)

        return reson["result"]

    def IP_Location(self, ip, coor="bd09ll"):
        '''
        高精度ip定位，用于ip定位
        :param ip: ip
        :param coor: 格式
        :return: 返回对应json数据包
        '''
        url = "http://api.map.baidu.com/highacciploc/v1?qcip="+ip+"&qterm=pc&extensions=1&coord="+coor+"&ak="+"仅支持AK校验，输入AK"
        url = urllib.quote(url, safe="!*'();:@&=+$,/?%#[]")

        resp = urllib2.urlopen(url)
        reson = json.loads(resp.read())

        self._check_official_errors(reson)

        return reson

    def Marker(self,  Latitude, Longitude):
        content = self.Get_LocationName(Latitude, Longitude)
        url = "http://api.map.baidu.com/marker?location="+str(Latitude)+","+str(Longitude)+"&title=我的位置&content="+content["region"].encode("utf-8")+"&coord_type=wgs84&output=html"
        return url

    def Get_sn(self, queryStr):
        '''
        SN Check Code
        :param queryStr: query url
        :return: sn
        '''
        encodedStr = urllib.quote(queryStr, safe="!*'();:@&=+$,/?%#[]")
        rawStr = encodedStr + self.sk
        return hashlib.md5(urllib.quote_plus(rawStr)).hexdigest()

    def _check_official_errors(self, json_data):
        if "status" in json_data and json_data["status"] != 0:
            raise OfficialAPIError("{}: {}".format(json_data["status"], json_data["message"].encode("utf-8")))

if __name__ == "__main__":
    ak = "你的AK"
    sk = "你的SK"
    coordtype = "bd09ll"
    s=map(ak,sk,coordtype)
    info = s.IP_Location(ip="你的ip")
    print info



