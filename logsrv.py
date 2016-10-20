# -*- coding: gbk -*-
import os
import os.path

LOG_DIR = "E:\\SecureCRTDownload\\logsrv.data"
#LOG_DIR = "/home/game/logsrv/data/"

def ReadLog(path, lines):
	f = open(path)
	lst = f.readlines()
	lines.extend(lst)
	print "��ȡ��%d����־ --From %s"%(len(lst), path)

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

def Parse():
	lines = []
	
	for parent, dirnames, filenames in os.walk(LOG_DIR):
		for filename in filenames:
			ReadLog(os.path.join(parent, filename), lines)
	print "������־����: %d"%len(lines)
	
	tdm = {}
	for line in lines:
	    dm = eval(line[21:-1])
	    tdm.setdefault(dm["type"],[]).append(dm)
	
	base_time = 1476633600	#2016-10-17 ���
	for i in xrange(3):
		print "====== %d�� ======"%(17 + i)
		stm, etm = base_time + i * 86400, base_time + (i + 1) * 86400
		print NewRoleLog(tdm[1], stm, etm)
		print LoginLog(tdm[2], stm, etm)
	
	return CheckLoginLogout(tdm)

if __name__ == "__main__":
	Parse()
