# -*- coding: gbk -*-
import os
import os.path
import json
import platform
import time
import random

STAT_BASETIME	= 1476633600	#2016-10-17 ���

FDIR = {
	"Linux"		: "/home/game/logsrv/data/",
	"Windows"	: "E:\\SecureCRTDownload\\logsrv.data",
}
def GetFileDir():
	oper_sys = platform.system()
	fdir = FDIR.get(oper_sys)
	if fdir == None:
		print "δ֪����ϵͳ"
		return None
	return fdir

def ReadFile(fp, tdm):
	n = 0
	with open(fp) as f:
		for line in f:
			dm = json.loads(line[21:-1])
			tdm.setdefault(dm["type"],[]).append(dm)
			n += 1
	print "��ȡ��%d����־ --From %s"%(n, fp)
	return n

def LoginLog(lst, stm, etm):
	line_cnt = 0
	rid_set = set()
	for dm in lst:
		if stm <= dm["tm"] < etm:
			line_cnt += 1
			rid_set.add(dm["rid"])
	return "��½��־����: %d, ��½ID��: %d"%(line_cnt, len(rid_set))

def NewRoleLog(lst, stm, etm):
	line_cnt = 0
	rid_set = set()
	for dm in lst:
		if stm <= dm["tm"] < etm:
			line_cnt += 1
			rid_set.add(dm["rid"])
	return "�½���ɫ��־����: %d, �½�ɫID��: %d"%(line_cnt, len(rid_set))

def GetLiveTimeData(tdm):
	rdm = {}
	for dm in tdm[2]:
		rdm.setdefault(dm["rid"], []).append((dm["tm"], 0))
	for dm in tdm[3]:
		rdm.setdefault(dm["rid"], []).append((dm["tm"], 1))
	for rid, lst in rdm.iteritems():
		lst.sort(key = lambda v : v[0])
	return rdm

def GetSecondString(tm, prec = 0):
	_tms = [("��", 60), ("����", 60), ("Сʱ", 24), ("��", 9999)]
	s = ""
	for i, t in enumerate(_tms):
		if i >= prec or tm < t[1]:
			v = tm % t[1]
			if v > 0:
				s = "%d%s"%(v, t[0]) + s
		tm /= t[1]
		if tm == 0:
			break
	return s

def PrintLogin(rdm, rand):
	if rand:
		lst = rdm.keys()
		n = len(lst)
		for _ in xrange(20):
			rid = lst[random.randint(0, n-1)]
			vlst = rdm[rid]
			_PrintLogin(rid, vlst)
	else:
		for rid, vlst in rdm.iteritems():
			_PrintLogin(rid, vlst)

def _PrintLogin(rid, vlst):
	print "-----------------------------------------"
	n = len(vlst) / 2
	if n > 0:
		ttm = 0
		for i in xrange(len(vlst)/2):
			s = ""
			tmpv = vlst[i*2:(i+1)*2]
			for tm, flag in tmpv:
				s += "%d, %s, %s\t\t" %(rid, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(tm)), ["��½ -->", "�ǳ� <--"][flag])
			if len(tmpv) == 2:
				IN, OUT = tmpv
				if IN[1] == 0 and OUT[1] == 1:
					livetm = OUT[0] - IN[0]
					if livetm >= 1200:
						vtm = livetm - 1200
						s += "%d, ��%03d����Ϸ: �ǳ�ʱ�� - ��½ʱ�� = %d; -1200, ��Чʱ��: %s(%d)"%(rid, i, livetm, GetSecondString(vtm), vtm)
						ttm += vtm
					else:
						s += "%d, ʱ�����, %d, %s, %s"%(rid, livetm, IN, OUT)
				else:
					s += "%d, ��Դ���, %s, %s"%(rid, IN, OUT)
			print s
		print rid, "������ʱ��: %s(%d)"%(GetSecondString(ttm), ttm)
	else:
		print rid, "���ݲ�����", vlst

def Parse(fdir):
	tdm = {}
	n = 0
	for root, dirs, files in os.walk(fdir):
		for fname in files:
			fp = os.path.join(root, fname)
			n += ReadFile(fp, tdm)
	print "������־����: %d"%n
	
	for i in xrange(3):
		print "====== %d�� ======"%(17 + i)
		stm, etm = STAT_BASETIME + i * 86400, STAT_BASETIME + (i + 1) * 86400
		print NewRoleLog(tdm[1], stm, etm)
		print LoginLog(tdm[2], stm, etm)
	
	rdm = GetLiveTimeData(tdm)
	PrintLogin(rdm, False)
	return rdm	#�����˹���½�ǳ�����

if __name__ == "__main__":
	fdir = GetFileDir()
	if fdir != None:
		Parse(fdir)
