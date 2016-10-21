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


MAX_LOOP_DAY		= 100
OFFLINE_PROTECT		= 19 * 60	#���߱���ʱ��

FDIR = {
	"Linux"		: "/home/game/logsrv/data/",
	"Windows"	: "E:\\SecureCRTDownload\\logsrv.data",
}
def GetFileDir():
	oper_sys = platform.system()
	fdir = FDIR.get(oper_sys)
	if fdir == None:
		print "δ֪����ϵͳ: %s"%oper_sys
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
	for dm in tdm[TYPE_LOGIN]:
		rdm.setdefault(dm["rid"], []).append((dm["tm"] - OFFLINE_PROTECT, 0, dm["log_seq"]))
	for dm in tdm[TYPE_LOGOUT]:
		rdm.setdefault(dm["rid"], []).append((dm["tm"] - OFFLINE_PROTECT, 1, dm["log_seq"]))
	for rid, lst in rdm.iteritems():
		lst.sort(key = lambda v : v[2])		#����seq��������ʱ����ľ��Ȳ�����
	return rdm

def GetSecondString(tm, prec = 0):
	_tms = [("��", 60), ("����", 60), ("Сʱ", 24), ("��", 9999)]
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

def PrintLogin(rdm, sample):
	if sample:
		lst = random.sample(rdm.keys())
	else:
		lst = rdm.keys()
	for rid in sorted(lst):
		_PrintLogin(rid, rdm[rid])

def _PrintLogin(rid, vlst):
	print "-----------------------------------------"
	n = len(vlst) / 2
	if n > 0:
		dm = {}
		ttm = 0
		for i in xrange(len(vlst)/2):
			s = ""
			tmpv = vlst[i*2:(i+1)*2]
			for tm, flag, _ in tmpv:
				s += "%d, %s, %s\t\t" %(rid, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(tm)), ["��½ -->", "�ǳ� <--"][flag])
			if len(tmpv) == 2:
				IN, OUT = tmpv
				if IN[1] == 0 and OUT[1] == 1:
					stm, etm = IN[0], OUT[0]
					livetm = etm - stm
					s += "%d, ��%03d����Ϸ: �ǳ�ʱ�� - ��½ʱ��( - %s) = %d"%(rid, i + 1, GetSecondString(OFFLINE_PROTECT), livetm)
					if livetm > 0:
						s += "(%s)"%GetSecondString(livetm)
						ttm += livetm
						UpdateLiveMap(stm, etm, dm)
					else:
						s += "ʱ�����, <= 0"
				else:
					s += "%d, ��%03d����Ϸ: ��Դ���, %s, %s"%(rid, i + 1, IN, OUT)
			print s
		print rid, "������ʱ��: %s(%d)"%(GetSecondString(ttm), ttm)
		for ntm in sorted(dm.keys()):
			print "%d ������(%s): %s(%d)"%(rid, time.strftime("%Y-%m-%d", time.localtime(ntm)), GetSecondString(dm[ntm]), dm[ntm])
	else:
		print rid, "���ݲ���������Ҫ��ȫ����ͳ��", vlst

def IsSameDay(tm, now):
	tm -= (tm - time.timezone)%86400		#����Ϊ����0ʱ
	now -= (now - time.timezone)%86400		#����Ϊ����0ʱ
	return tm == now

def GetDay(tm):
	return tm - (tm - time.timezone)%86400

def GetDayEnd(tm):
	return tm - (tm - time.timezone)%86400 + 86400

def UpdateLiveMap(stm, etm, dm):
	for _ in xrange(MAX_LOOP_DAY):
		if stm >= etm:
			break
		dm[GetDay(stm)] = dm.get(GetDay(stm), 0) + (min(etm, GetDayEnd(stm)) - stm)
		stm = GetDayEnd(stm)
	else:
		raise "������̫��"
	return dm

def Parse(fdir):
	tdm = {}
	n = 0
	for root, dirs, files in os.walk(fdir):
		for fname in sorted(files):
			fp = os.path.join(root, fname)
			n += ReadFile(fp, tdm)
	print "������־����: %d"%n
	
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
		raise "������̫��"
	rdm = GetLiveTimeData(tdm)
	PrintLogin(rdm, False)
	return rdm	#�����˹���½�ǳ�����

if __name__ == "__main__":
	fdir = GetFileDir()
	if fdir != None:
		Parse(fdir)
