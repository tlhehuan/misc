# -*- coding: gbk -*-

import os
import os.path
import json
import platform
import time
import random

#日志类型定义，参考protocol_logsrv.py
TYPE_NEW_ROLE		= 0x01
TYPE_LOGIN		= 0x02
TYPE_LOGOUT		= 0x03

MAX_LOOP_DAY		= 100		#最大计算天数
OFFLINE_PROTECT		= 19 * 60	#离线保护时间

def GetFileDir():
	FDIR = {
		"Linux"		: "/home/game/logsrv/data/",
		"Windows"	: "E:/SecureCRTDownload/logsrv/data/",
	}
	
	oper_sys = platform.system()
	fdir = FDIR.get(oper_sys)
	if fdir == None:
		print "未知操作系统: %s"%oper_sys
		return None
	return fdir

def ReadFile(fp, tdm):
	n = 0
	with open(fp) as f:
		for line in f:
			dm = json.loads(line[21:-1])
			seq = line[:20]
			dm["log_seq"] = seq
			tdm.setdefault(dm["type"],[]).append(dm)
			n += 1
	print "读取到%d行日志 --From %s"%(n, fp)
	return n

def LoginLog(lst, stm, etm):
	n = 0
	rid_set = set()
	for dm in lst:
		if stm <= dm["tm"] < etm:
			n += 1
			rid_set.add(dm["rid"])
	return "登陆日志行数: %d, 登陆ID数: %d"%(n, len(rid_set))

def NewRoleLog(lst, stm, etm):
	n = 0
	rid_set = set()
	for dm in lst:
		if stm <= dm["tm"] < etm:
			n += 1
			rid_set.add(dm["rid"])
	return "新建角色日志行数: %d, 新角色ID数: %d"%(n, len(rid_set))

def GetLiveData(tdm):
	rdm = {}
	for dm in tdm[TYPE_LOGIN]:
		rdm.setdefault(dm["rid"], []).append((dm["tm"] - OFFLINE_PROTECT, 0, dm["log_seq"]))
	for dm in tdm[TYPE_LOGOUT]:
		rdm.setdefault(dm["rid"], []).append((dm["tm"] - OFFLINE_PROTECT, 1, dm["log_seq"]))
	for rid, lst in rdm.iteritems():
		lst.sort(key = lambda v : v[2])		#根据seq排序（整数时间戳的精度不够）
	return rdm

def PrintLiveTime(rdm, sample):
	if sample:
		lst = random.sample(rdm.keys())
	else:
		lst = rdm.keys()
	
	for rid in sorted(lst):
		DoPrintLiveTime(rid, rdm[rid])

def DoPrintLiveTime(rid, vlst):
	dlm = {}	#日在线时长
	total = 0	#总在线时长
	
	print "-----------------------------------------"
	n, rem = divmod(len(vlst), 2)
	for i in xrange(n):
		s = "%d 第%03d次游戏: "%(rid, i + 1)
		
		(stm, slt, _), (etm, elt, _) = vlst[i*2:(i+1)*2]
		assert slt == 0 and elt == 1 and stm < etm
		
		stms = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stm))
		etms = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(etm))
		s += "%s --> %s, " %(stms, etms)
		
		livetm = etm - stm
		total += livetm
		s += "登出时间 - 登陆时间 = %d(%s)"%(livetm, GetSecondString(livetm))
		
		AddLiveMap(stm, etm, dlm)
		print s
	
	if rem > 0:
		stm, slt, _ = vlst[-1]
		s = "%d 第%03d次游戏: "%(rid, n + 1)
		stms = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stm))
		s += "%s --> (尚未登出)" %stms
		print s
	
	for ntm in sorted(dlm.keys()):
		date = time.strftime("%Y-%m-%d", time.localtime(ntm))
		print "%d 日在线(%s): %d(%s)"%(rid, date, dlm[ntm], GetSecondString(dlm[ntm]))
	if total > 0:
		print "%d 总在线时长: %d(%s)"%(rid, total, GetSecondString(total))

def AddLiveMap(stm, etm, dlm):
	for _ in xrange(MAX_LOOP_DAY):
		if stm >= etm:
			break
		dlm[GetDay(stm)] = dlm.get(GetDay(stm), 0) + (min(etm, GetDayEnd(stm)) - stm)
		stm = GetDayEnd(stm)
	else:
		raise "总天数太长"
	return dlm

def Check_Main(fdir):
	tdm = {}	#日志数据
	
	#读取
	n = 0
	for root, dirs, files in os.walk(fdir):
		for fname in sorted(files):
			fp = os.path.join(root, fname)
			n += ReadFile(fp, tdm)
	print "所有日志行数: %d"%n
	
	#计算每天的新角色数量、登陆数量
	stm = min(dm["tm"] for lst in tdm.values() for dm in lst)
	etm = max(dm["tm"] for lst in tdm.values() for dm in lst)
	for _ in xrange(MAX_LOOP_DAY):
		if stm >= etm:
			break
		date = time.strftime("%Y-%m-%d", time.localtime(stm))
		print date, NewRoleLog(tdm[TYPE_NEW_ROLE], GetDay(stm), GetDayEnd(stm))
		print date, LoginLog(tdm[TYPE_LOGIN], GetDay(stm), GetDayEnd(stm))
		stm = GetDayEnd(stm)
	else:
		raise "总天数太长"
	
	#计算在线时间
	rdm = GetLiveData(tdm)
	PrintLiveTime(rdm, False)
	return rdm


###########################################################
#工具函数
###########################################################
def GetSecondString(tm, prec = 0):
	_tms = [("秒", 60), ("分钟", 60), ("小时", 24), ("天", 9999)]
	s = ""
	for i, (u, n) in enumerate(_tms):
		if tm < n or i >= prec:
			v = tm % n
			if v > 0:
				s = "%d%s"%(v, u) + s
		tm /= n
		if tm == 0:
			break
	return s

def IsSameDay(tm, now):
	tm -= (tm - time.timezone) % 86400		#调整为当日0时
	now -= (now - time.timezone) % 86400		#调整为当日0时
	return tm == now

def GetDay(tm):
	return tm - (tm - time.timezone) % 86400

def GetDayEnd(tm):
	return tm - (tm - time.timezone) % 86400 + 86400

if __name__ == "__main__":
	fdir = GetFileDir()
	if fdir != None:
		Check_Main(fdir)
