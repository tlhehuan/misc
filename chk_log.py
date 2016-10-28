# -*- coding: gbk -*-

import os
import os.path
import json
import platform
import time
import random

#��־���Ͷ��壬�ο�protocol_logsrv.py
TYPE_NEW_ROLE		= 0x01
TYPE_LOGIN		= 0x02
TYPE_LOGOUT		= 0x03

MAX_LOOP_DAY		= 100		#����������
OFFLINE_PROTECT		= 19 * 60	#���߱���ʱ��

def GetFileDir():
	FDIR = {
		"Linux"		: "/home/game/logsrv/data/",
		"Windows"	: "E:/SecureCRTDownload/logsrv/data/",
	}
	
	oper_sys = platform.system()
	fdir = FDIR.get(oper_sys)
	if fdir == None:
		print "δ֪����ϵͳ: %s"%oper_sys
		return None
	return fdir

def ReadFile(fp, dm_lst):
	n = 0
	ts = set([TYPE_NEW_ROLE, TYPE_LOGIN, TYPE_LOGOUT])
	
	with open(fp) as f:
		for line in f:
			n += 1
			dm = json.loads(line[21:-1])
			if dm["type"] in ts:
				dm_lst.append(dm)
	
	print "��ȡ��%d����־ --From %s"%(n, fp)
	return n

def LoginLog(lst, stm, etm):
	n = 0
	rid_set = set()
	for dm in lst:
		if stm <= dm["tm"] < etm:
			n += 1
			rid_set.add(dm["rid"])
	return "��½��־����: %d, ��½ID��: %d"%(n, len(rid_set))

def NewRoleLog(lst, stm, etm):
	n = 0
	rid_set = set()
	for dm in lst:
		if stm <= dm["tm"] < etm:
			n += 1
			rid_set.add(dm["rid"])
	return "�½�ɫ��־����: %d, �½�ɫID��: %d"%(n, len(rid_set))

def PrintLiveTime(rid, vlst):
	dlm = {}	#������ʱ��
	total = 0	#������ʱ��
	
	print "-----------------------------------------"
	n, rem = divmod(len(vlst), 2)
	for i in xrange(n):
		s = "%d ��%03d����Ϸ: "%(rid, i + 1)
		
		sdm = vlst[i * 2]
		edm = vlst[i * 2 + 1]
		assert sdm["type"] == TYPE_LOGIN and edm["type"] == TYPE_LOGOUT
		
		stm = sdm["tm"]
		etm = edm["tm"] - OFFLINE_PROTECT	#�۳����߱���ʱ��
		stms = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stm))
		etms = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(etm))
		s += "%s --> %s, "%(stms, etms)
		
		livetm = etm - stm
		s += "�ǳ�ʱ�� - ��½ʱ�� = %d(%s)"%(livetm, FormatTimeLength(livetm))
		if livetm < 0:
			s += "\t�������߱���ʱ�䣬���Բ���"
			print s
			continue
		
		AddLiveMap(stm, etm, dlm)
		total += livetm
		print s
	
	if rem > 0:
		sdm = vlst[-1]
		stm = sdm["tm"]
		s = "%d ��%03d����Ϸ: "%(rid, n + 1)
		stms = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stm))
		s += "%s --> (��δ�ǳ�)"%stms
		print s
	
	for ntm in sorted(dlm.keys()):
		date = time.strftime("%Y-%m-%d", time.localtime(ntm))
		print "%d ������(%s): %d(%s)"%(rid, date, dlm[ntm], FormatTimeLength(dlm[ntm]))
	
	if total > 0:
		print "%d ������ʱ��: %d(%s)"%(rid, total, FormatTimeLength(total))

def AddLiveMap(stm, etm, dlm):
	for _ in xrange(MAX_LOOP_DAY):
		if stm >= etm:
			break
		
		dlm[GetToday(stm)] = dlm.get(GetToday(stm), 0) + (min(etm, GetNextDay(stm)) - stm)
		stm = GetNextDay(stm)
	else:
		raise "������̫��"
	
	return dlm

def Check_Main(fdir):
	dm_lst = []	#ԭʼ����
	#��ȡ
	n = 0
	for root, dirs, files in os.walk(fdir):
		for fname in sorted(files):
			fp = os.path.join(root, fname)
			n += ReadFile(fp, dm_lst)
	print "������־����: %d\n����������: %d"%(n, len(dm_lst))
	
	#����ÿ����½�ɫ��������½����
	stm = min(dm["tm"] for dm in dm_lst)
	etm = max(dm["tm"] for dm in dm_lst)
	new_lst = [dm for dm in dm_lst if dm["type"] == TYPE_NEW_ROLE]
	log_lst = [dm for dm in dm_lst if dm["type"] == TYPE_LOGIN]
	for _ in xrange(MAX_LOOP_DAY):
		if stm >= etm:
			break
		
		date = time.strftime("%Y-%m-%d", time.localtime(stm))
		print date, NewRoleLog(new_lst, GetToday(stm), GetNextDay(stm))
		print date, LoginLog(log_lst, GetToday(stm), GetNextDay(stm))
		stm = GetNextDay(stm)
	else:
		raise "������̫��"
	
	#��������ʱ��
	rdm = {}
	for dm in dm_lst:
		if dm["type"] in (TYPE_LOGIN, TYPE_LOGOUT):
			rdm.setdefault(dm["rid"], []).append(dm)
	for rid in sorted(rdm.keys()):			#����ɫID˳���ӡ
		PrintLiveTime(rid, rdm[rid])
	return rdm


###########################################################
#���ߺ���
###########################################################
def GetToday(tm):	#����0��
	return tm - (tm - time.timezone) % 86400

def GetNextDay(tm):	#����0��
	return tm - (tm - time.timezone) % 86400 + 86400

def IsSameDay(x, y):
	return GetToday(x) == GetToday(y)

def FormatTimeLength(tm):
	FMT = [("��", 60), ("����", 60), ("Сʱ", 24), ("��", 9999)]
	
	if tm < 0:
		ps = "-"
		tm = -tm
	else:
		ps = ""
	
	s = ""
	for i, (u, n) in enumerate(FMT):
		tm, v = divmod(tm, n)
		s = "%d%s"%(v, u) + s
		if tm == 0:
			break
	
	return ps + s

if __name__ == "__main__":
	fdir = GetFileDir()
	if fdir != None:
		Check_Main(fdir)
