# -*- coding: gbk -*-
import os
import os.path
import json
import platform

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

def CheckLoginLogout(tdm):
	rdm = {}
	for dm in tdm[2]:
		rdm.setdefault(dm["rid"], []).append((dm["tm"], 0))
	for dm in tdm[3]:
		rdm.setdefault(dm["rid"], []).append((dm["tm"], 1))
	for rid, lst in rdm.iteritems():
		lst.sort(key = lambda v : v[0])
	for rid, vlst in rdm.items():
		for idx in xrange(0, len(vlst)-1):
			if vlst[idx][1] == vlst[idx + 1][1]:
				print "��½-�ǳ��쳣", rid, vlst
				break
	return rdm

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
	
	ldm = CheckLoginLogout(tdm)
	return ldm	#�����˹���½�ǳ�����

if __name__ == "__main__":
	fdir = GetFileDir()
	if fdir != None:
		Parse(fdir)
