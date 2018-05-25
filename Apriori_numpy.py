#coding:utf-8
import numpy as np

class Apriori:

	def __init__(self,min_support,min_confidence,max_length):
		self.min_support=min_support  # 最小支持度  (ab)/n
		self.min_confidence=min_confidence  # 最小置信度  (ab)/a
		self.max_length=max_length   # 频繁项的最大长度

	def count(self,filename='apriori.txt'):
		self.total=0  # 数据总行数
		items={}    # 物品清单  {'book':5,...}

		with open(filename) as f:
			for l in f:
				self.total+=1
				for i in l.strip().split(','):  # 逗号隔开
					if i in items:
						items[i]+=1
					else:
						items[i]=1

		# 物品清单去重  映射到ID
		# 计算支持度 并去掉支持度小的部分
		self.items={i:1.0*j/self.total for i,j in items.items() if 1.0*j/self.total>self.min_support}
		self.item2id={j:i for i,j in enumerate(self.items)}

		# 物品清单的0-1矩阵
		self.D=np.zeros((self.total,len(items)),dtype=bool)

		# 重新遍历文件，得到物品清单的0-1矩阵
		with open(filename) as f:
			for n,l in enumerate(f):
				for i in l.strip().split(','):
					if i in self.items:
						self.D[n,self.item2id[i]]=True


	def find_rules(self,filename='apriori.txt'):
		# 统计文件
		self.count(filename)
		# 记录每一步的频繁项集合  
		# 初始 单个物品
		rules=[{(i,):j for i,j in self.items.items()}]
		l=0  # 当前步的频繁项的物品数

		# l=0  频繁项长度1  l=1 ...2  

		while rules[-1] and l+1<self.max_length:  # 停止条件 未加入任何新频繁项
			rules.append({})
			# 对每个k频繁项按字典顺序排序（核心）
			keys=sorted(rules[-2].keys())
			num=len(rules[-2])
			l+=1

			for i in range(num):  # 遍历k个频繁项对
				for j in range(i+1,num):
					# 如果前面k-1个重叠，那么这两个k频繁项就可以组合成一个k+1频繁项
					if keys[i][:l-1]==keys[j][:l-1]:
						_=keys[i]+(keys[j][l-1],)
						_id=[self.item2id[k] for k in _]
						# 核心 通过0-1矩阵的子矩阵 第1维的连乘 得到共现次数
						support=1.*sum(np.prod(self.D[:,_id],1))/self.total
						if support>self.min_support:  # _的支持度大于min_support 加入rules
							rules[-1][_]=support

		# 遍历每一个频繁项 计算置信度
		results={}
		# rules[0] 是单物品
		for n,rule in enumerate(rules[1:]):
			for r,v in rule.items():
				for i,_ in enumerate(r):
					x=r[:i]+r[i+1:]
					confidence=v/rules[n][x]  # 不同排列的置信度
					if confidence>self.min_confidence:
						# 置信度  支持度
						results[x+(r[i],)]=(confidence,v)
						# 按置信度 降序排列
		return sorted(results.items(),key=lambda x:-x[1][0])


import time

# test
# 1. 自己实现
t0=time.time()
model=Apriori(0.06,0.75,3)
res=model.find_rules('apriori.txt')
for item in res:
	print item
t1=time.time()
print 'my model cost time:%ss' %(t1-t0)

# py第三方包  pip install apyori==1.1.1
from apyori import apriori
t0=time.time()
documents=[]
with open('apriori.txt') as f:
	for line in f:
		documents.append(line.strip().split(','))
res=list(apriori(documents,min_support=0.06,min_confidence=0.75,max_length=3))
for items in res:
	item=items.ordered_statistics[0]
	print list(item.items_base),list(item.items_add),(item.confidence,items.support)
t1=time.time()
print 'apyori apriori cost time:%ss' %(t1-t0)