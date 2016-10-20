# -*- coding: gbk -*-
import os
import os.path
import json
import platform

if platform.system() == "Linux":
	LOG_DIR = "/home/game/logsrv/data/"
else:
	LOG_DIR = "E:\\SecureCRTDownload\\logsrv.data"

def ReadLog(path, tdm):
	n = 0
	with open(path) as f:
		for line in f:
			dm = json.loads(line[21:-1])
			tdm.setdefault(dm["type"],[]).append(dm)
			n += 1
	print "��ȡ��%d����־ --From %s"%(n, path)
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

def Parse():
	tdm = {}
	n = 0
	for parent, dirnames, filenames in os.walk(LOG_DIR):
		for filename in filenames:
			n += ReadLog(os.path.join(parent, filename), tdm)
	print "������־����: %d"%n
	
	base_time = 1476633600	#2016-10-17 ���
	for i in xrange(3):
		print "====== %d�� ======"%(17 + i)
		stm, etm = base_time + i * 86400, base_time + (i + 1) * 86400
		print NewRoleLog(tdm[1], stm, etm)
		print LoginLog(tdm[2], stm, etm)
	
	ldm = CheckLoginLogout(tdm)
	return ldm

if __name__ == "__main__":
	Parse()
