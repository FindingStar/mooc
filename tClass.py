import requests
import pymysql
import json

THESESSIONID="ab06e50957fc4f88bf50e64adf759bfb"
BASE_HEADERS={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
		"Host":"www.icourse163.org",
		"Connection":"keep-alive",
		"Accept-Encoding":"gzip, deflate, br",
		"Accept-Language":"zh-CN,zh;q=0.9",
		"Origin":"https://www.icourse163.org",
		"Accept":"*/*"
	}
BASE_COOKIES={"EDUWEBDEVICE":"6ad321f5006a415580593979ff410de6",
		"hb_MA-A976-948FFA05E931_source":"www.baidu.com",
		"WM_TID":"%2Bibl4k%2FrbXtEAAQVBAMo1m21ncLP1ChB",
		"bpmns":"1",
		"WM_NI":"2z5MBQHO2Hooum89X5vd%2BN0%2FS7WztQoky%2FDWbtIbFFlTYtLx317eXjaWFIcMAckt%2Fa2nYF%2FFUSADpFdJwlEGu3I7Lkr7PIUl31DcVw0NWJOVMSKrzAd6IV0Z7sdC7lAEanI%3D",
		"WM_NIKE":"9ca17ae2e6ffcda170e2e6eeb1d53cb2eca5b8ef4e949e8eb7d85e829a9faeb768ae94bed0f75b94aaae85c92af0fea7c3b92abb8bfbadf869a197bf86c14f898ea78ceb7fa7e9a0d7b8408888ffaacd498e9ba7d2d96798abf98df247818ea7ccd852a997a785d86885a9a589f972aaacad8ad33390ebbbd6d6688694bd94e86af1978a8ac548e9a7ad82d233f48981d8f73f87aaa4d1db6eed90a4a3f866a3adbd95c252e99ca4a9e944ac97fdacd04ebb8b9d9bc837e2a3",
		"__utmz":"63145271.1552116403.26.17.utmcsr=baidu|utmccn=(organic)|utmcmd=organic",
		"NTESSTUDYSI":THESESSIONID,
		"__utmc":"63145271",
		"STUDY_SESS":"0yxK6x5T/ziIyc/PAufoGHqgFus5BrUmmwL9ReiNZ24Q0C7vLfMaZ6yys6anMOcjmzyVpDYUs4TATWCLfG5W+n6jcShuPIYcMkLTZ48qpGc5F3+lFk3nGZesQF76cgsBodRuOphIp4+mQcxhp6U3vFFulgoQkUGA5jKTAu0PXggGtvdDMf+W+TeYYpWAgrO1+P6MxCmnJEvne6pPMc9TTJJnThNrM7aj0X5LVpSBvjYKWxskjOWX+NGuGvX9Zu6soCPGDth+Om3e3zBe8+uTCWHTEDOAP9ec8rdI9htT7ptKlOh/Gwx6G1S/X4FQ7qd/fDmKepME9pXcEgvbEpiKxPNPf4xyU+UCQctLAK0Yf8xuLocEkebo85o8l479VnO6",
		"STUDY_INFO":"UID_778EEE8FE8ED1F4D510F4E4BA7B3C4A4|4|1036064017|1552715909131",
		"NETEASE_WDA_UID":"1036064017#|#1516627330454"
	}

# 连接db
def connectDb():
	connection=pymysql.connect(host='39.107.79.62',
		user="root",
		password="root",
		database="xiaochengxu",
		charset="utf8")
	return connection

# json 转字典
def jsonToDict(jsonStr):
	dic=json.loads(jsonStr)
	return dic

# 1 .获取全部课程	
def getSubjects():
	
	url="https://www.icourse163.org/web/j/mocCourseCategoryBean.getCategByType.rpc?csrfKey="+THESESSIONID
	
	#eee 这样改变的也是 全局....
	headers=BASE_HEADERS
	headers.update({"Content-Type":"application/x-www-form-urlencoded",
		"edu-script-token":THESESSIONID,
		"Referer":"https://www.icourse163.org/category/all"})
	cookies=BASE_COOKIES
	cookies.update({"hasVolume":"true",
		"videoVolume":"0.8"})
	data={"type":"4"}
	
	subjectsRes=requests.post(url,data=data,headers=headers,cookies=cookies)
	
	subjectsDict=jsonToDict(subjectsRes.text)
	
	subjectsList=subjectsDict["result"]
	
	subjectConnection=connectDb()
	subjectCursor = subjectConnection.cursor()
	sql = "SELECT * FROM subject WHERE subject_id=%s"

	for subject in subjectsList:
		print(str(subject["id"])+"---------"+subject["name"]+"--------"+subject["mobIcon"])
		queryResCount=subjectCursor.execute(sql,subject["id"])
		if(queryResCount==0):
			insertSql="INSERT INTO subject (subject_id,subject_name,icon_url) VALUES(%s,%s,%s)"
			queryResCount=subjectCursor.execute(sql,(subject["id"],subject["name"],subject["mobIcon"]))	
			subjectConnection.commit()	
		#2 获取subject下的course
		print("获取   "+subject["name"]+"   下课程")
		counts=getCourseOfSubject(subject["id"])		
		print(subject["name"]+"-------"+str(counts)+"个课程更新成功\n")
	subjectConnection.close()

	
# 2. 获取某个subject下的课程。 (subjectId，refer指向)
def getCourseOfSubject(subjectId):
	
	#  后期 递归调用 好一点， 
	pageIndex=1
	url="https://www.icourse163.org/web/j/courseBean.getCoursePanelListByFrontCategory.rpc?csrfKey="+THESESSIONID
	#edu 那个还是sessionId
	
	courseConnection=connectDb()
	courseCursor=courseConnection.cursor()
	querySql="SELECT *FROM subject WHERE subject_id=%s"
	courseCursor.execute(querySql,subjectId)
	#返回元组
	result=courseCursor.fetchall()
	result=result[0]
	referName=result[4]
	
	headers=BASE_HEADERS.update({"Content-Type":"application/x-www-form-urlencoded",
		"edu-script-token":THESESSIONID,
		"Referer":"https://www.icourse163.org/category/"+referName})	
	cookies=BASE_COOKIES
	#这里直接传 int 就好。感觉像是后期绑定的那种，自动添加或者取出“”
	data={"categoryId":subjectId,
		"type":"30",
		"orderBy":"0",
		"pageIndex":pageIndex,
		"pageSize":"20"}
	coursesRes=requests.post(url,data=data,headers=headers,cookies=cookies)
	coursesDict=jsonToDict(coursesRes.text)
	coursesDict=coursesDict["result"]
	#subject 的 page信息
	subjectPageInfoDict=coursesDict["pagination"]
	
	
	#第一页默认
	for course in coursesDict["result"]:
		print("------第"+str(pageIndex)+"页----"+"课程名称：   "+course["name"]+"------课程Id:     "+str(course["currentTermId"]))
		
		term=course["termPanel"]
		school=course["schoolPanel"]
		querySql1="SELECT * FROM course WHERE course_id=%s"
		querySql2="SELECT * FROM source WHERE course_id=%s"
		# 查询返回 记录数
		resCount1=courseCursor.execute(querySql1,course["currentTermId"])
		resCount2=courseCursor.execute(querySql2,course["currentTermId"])
		if(resCount2==0):
			if(resCount1==0):
				sql="INSERT INTO course (name,course_id,img_url,in_school_id,learner_count,school_id,introduce,lessons_count)VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
				courseCursor.execute(sql,(course["name"],course["currentTermId"],course["imgUrl"],course["id"],course["learnerCount"],course["schoolId"],term["jsonContent"],term["lessonsCount"]))
			
			referName=(school["shortName"])+"-"+str(course["id"])
			print("----------获取课程   "+course["name"]+"  课件资源")
			
			getSource(course["currentTermId"],referName)
		courseConnection.commit()
		
	print("------第"+str(pageIndex)+"页 更新数据库成功")
		
	pageIndex=subjectPageInfoDict["pageIndex"]+1
	totalPageCount=subjectPageInfoDict["totlePageCount"]
	totalCount=subjectPageInfoDict["totleCount"]
	
	print("***共有  "+str(totalPageCount)+"  页***")	
	for index in range(2,totalPageCount+1):
		data={"categoryId":subjectId,
			"type":"30",
			"orderBy":"0",
			"pageIndex":pageIndex,
			"pageSize":"20"}
		coursesRes=requests.post(url,data=data,headers=headers,cookies=cookies)
		coursesDict=jsonToDict(coursesRes.text)
		coursesDict=coursesDict["result"]
		subjectPageInfoDict=coursesDict["pagination"]

		for course in coursesDict["result"]:
			print("------第"+str(pageIndex)+"页-----"+"课程名称：   "+course["name"]+"------课程Id:     "+str(course["currentTermId"]))
			
			term=course["termPanel"]
			school=course["schoolPanel"]
			querySql1="SELECT * FROM course WHERE course_id=%s"
			querySql2="SELECT * FROM source WHERE course_id=%s"
			# 查询返回 记录数
			resCount1=courseCursor.execute(querySql1,course["currentTermId"])
			resCount2=courseCursor.execute(querySql2,course["currentTermId"])
			if(resCount2==0):
				if(resCount1==0):
					sql="INSERT INTO course (name,course_id,img_url,in_school_id,learner_count,school_id,introduce,lessons_count)VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
					courseCursor.execute(sql,(course["name"],course["currentTermId"],course["imgUrl"],course["id"],course["learnerCount"],course["schoolId"],term["jsonContent"],term["lessonsCount"]))
			
				referName=(school["shortName"])+"-"+str(course["id"])
				print("----------获取课程   "+course["name"]+"  课件资源")
				getSource(course["currentTermId"],referName)
			courseConnection.commit()
		
			
		print("------第"+str(pageIndex)+"页 更新数据库成功")
			
		pageIndex=subjectPageInfoDict["pageIndex"]+1
	
	courseConnection.close()
	
	return totalCount
	
# 3 获取某课程课件全部资源信息 (courseId,refer)
def getSource(courseId,referName):
	url="https://www.icourse163.org/dwr/call/plaincall/CourseBean.getLastLearnedMocTermDto.dwr"
	#为什么这里 就能这样更新？
	headers=BASE_HEADERS

	headers.update({"Content-Type":"text/plain",
		"Referer":"https://www.icourse163.org/learn/"+referName})
	data={"callCount":"1",
		"scriptSessionId":"${scriptSessionId}190",
		"httpSessionId":THESESSIONID,
		"c0-scriptName":"CourseBean",
		"c0-methodName":"getLastLearnedMocTermDto",
		"c0-id":"0",
		"c0-param0":"number:"+str(courseId),
		"batchId":"1552116862756"}
	sourceStr=requests.post(url,data=data,headers=headers,cookies=BASE_COOKIES).text
	
	sourceStr=sourceStr.replace(" ","").replace("\r\n","")
	
	index1=sourceStr.find("s0.videoId=null;")
	index2=sourceStr.find("dwr.engine")
	sourceStr=sourceStr[index1:index2]
	
	sourceStr=sourceStr.replace("=\"","=").replace("\";",";")
	#有一节课 编程课题目=  uFF08n=3
	sourceStr=sourceStr.replace("uFF08n=3","uFF08n 3")
	sourceStr=sourceStr.replace("=",'":"').replace(";",'","')
	
	sourceStr="{\""+sourceStr
	sourceStr=sourceStr[0:len(sourceStr)-2]
	sourceStr=sourceStr+"}"
	
	# 英语课  有的 字符串里面有 /‘  影响
	sourceStr=sourceStr.replace("\\'","  ")
	
	sourceDict=json.loads(sourceStr)
	
	sourceConnection=connectDb()
	sourceCursor=sourceConnection.cursor()
	usedIds=[]
	
	for key in sourceDict.keys():
		if("contentId" in key):
			if((sourceDict[key]!="null")&(sourceDict[key]!="")):
			
				curId=key[0:len(key)-10]
		
				usedIds.append(curId)
	
	j=1
	aDic={}
	verDic={}
	for key in sourceDict.keys():
		for i in range(0,len(usedIds)):
			if(usedIds[i] in key):
				
				if(("contentId" in key) or ("id" in key)or("contentType" in key)or("name" in key)or("termId" in key)):
					
					j=j+1
					aDic[key]=sourceDict[key]
					
					# 防止接连的 重复信息。 如 连着写了两次 so.content 
					if(aDic!={}):
						if(key not in verDic.keys()):
							verDic[key]=aDic[key]
						else:
							j=j-1	
					
					if(j>5):	
						print(key+" "+verDic[key])
						j=1
						contentId=""
						contentType=""
						name=""
						courseId=""
						unknownId=""
						for aKey in aDic.keys():
							if("contentId" in aKey):
								
								contentId=aDic[aKey]
							if("contentType" in aKey):
								contentType=aDic[aKey]
							if("id" in aKey):
								unknownId=aDic[aKey]
							if("name" in aKey):
								name=aDic[aKey]
							if("termId" in aKey):
								courseId=aDic[aKey]
						
						querySql="SELECT * FROM source WHERE content_id=%s"
						print("------------"+contentId+"----"+contentType+"-----"+name+"-----"+courseId)
						resCount=sourceCursor.execute(querySql,contentId)
						if(resCount==0):
							
							insertSql="INSERT INTO source (content_id,content_type,name,course_id,unknown_id)VALUES(%s,%s,%s,%s,%s)"
							
							if(contentId=="null"):
								contentId="0"
							sourceCursor.execute(insertSql,(contentId,contentType,name,courseId,unknownId))
							sourceConnection.commit()
							if(contentType=="1"):
								
								print("--------------获取这节课的视频")
								getVideo(contentId,unknownId,referName)
							if(contentType=="3"):
								print("--------------获取这节课的文档")
								getDoc(contentId,unknownId,referName)
						aDic={}
					
			
	print("----------获取 当前课程课件资源 完成")
	sourceConnection.close()
	
# 3.1 获取某个课程某节课的视频(videoId, unKnownId,refer)
def getVideo(videoId,unknownId,referName):
	
	url="https://www.icourse163.org/dwr/call/plaincall/CourseBean.getLessonUnitLearnVo.dwr"
	headers=BASE_HEADERS.update({"Content-Type":"text/plain",
		"Referer":"https://www.icourse163.org/learn/"+referName})
	data={"callCount":"1",
		"scriptSessionId":"${scriptSessionId}190",
		"httpSessionId":THESESSIONID,
		"c0-scriptName":"CourseBean",
		"c0-methodName":"getLessonUnitLearnVo",
		"c0-id":"0",
		"c0-param0":"number:"+str(videoId),
		"c0-param1":"number:1",
		"c0-param2":"number:0",
		"c0-param3":"number:"+str(unknownId),
		"batchId":"1552116862756"}
	videoStr=requests.post(url,data=data,headers=headers,cookies=BASE_COOKIES).text
	
	index1=videoStr.find("mp4SdUrl=")
	videoStr=videoStr[index1+10:len(videoStr)]

	index2=videoStr.find("?ak")
	videoUrl=videoStr[0:index2]
	index3=videoStr.find("videoImgUrl=")
	index4=videoStr.find("videoProtectedDataDto")
	videoImgUrl=videoStr[index3+13:index4-5]
	
	videoConnection=connectDb()
	videoCursor=videoConnection.cursor()
	
	querySql="SELECT *FROM source WHERE content_id=%s"
	queryResCount=videoCursor.execute(querySql,videoId)
	
	if(queryResCount!=0):
		updateSql="UPDATE source SET content_url=%s,img_url=%s WHERE content_id=%s"
		videoCursor.execute(updateSql,(videoUrl,videoImgUrl,videoId))
		videoConnection.commit()
		
	print("--------------mp4SHD地址："+videoUrl+"\n"+"--------------视频图片地址："+videoImgUrl)	
	videoConnection.commit()
	videoConnection.close()
	
# 3.1 获取某个课程某节课的文档(docId, unKnownId,refer)
def getDoc(docId,unknownId,referName):
	url="https://www.icourse163.org/dwr/call/plaincall/CourseBean.getLessonUnitLearnVo.dwr"
	headers=BASE_HEADERS.update({"Content-Type":"text/plain",
		"Referer":"https://www.icourse163.org/learn/"+referName})
	data={"callCount":"1",
		"scriptSessionId":"${scriptSessionId}190",
		"httpSessionId":THESESSIONID,
		"c0-scriptName":"CourseBean",
		"c0-methodName":"getLessonUnitLearnVo",
		"c0-id":"0",
		"c0-param0":"number:"+str(docId),
		"c0-param1":"number:3",
		"c0-param2":"number:0",
		"c0-param3":"number:"+str(unknownId),
		"batchId":"1552116862756"}
	docStr=requests.post(url,data=data,headers=headers,cookies=BASE_COOKIES).text
	index1=docStr.find("textOrigUrl")
	index2=docStr.find("textPageWhRatio")
	docUrl=docStr[index1+13:index2-2]
	
	docConnection=connectDb()
	docCursor=docConnection.cursor()
	querySql="SELECT *FROM source WHERE content_id=%s"
	queryResCount=docCursor.execute(querySql,docId)
	if(queryResCount!=0):
		updateSql="UPDATE source SET content_url=%s WHERE content_id=%s"
		docCursor.execute(updateSql,(docUrl,docId))
		docConnection.commit()
	
	docConnection.commit()
	docConnection.close()
	
	print("--------------这节课文档 地址： "+docUrl)
	

getSubjects()
