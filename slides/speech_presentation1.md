# Presentation 1 — 演讲稿 / Speaking script

10 分钟，12 页。每页先中文、后英文，讲其中一种即可。
Timing target ~50 s per content slide; title / question slides are quick.

**讲者分工 (4 人 / 4 speakers)** — 3 人版见文末
- 讲者 A：Slide 1–3
- 讲者 B：Slide 4–6
- 讲者 C：Slide 7–9
- 讲者 D：Slide 10–12

---

## Slide 1 — 标题 / Title  ·  ~20 s  ·  讲者 A

**中文**
大家好。我们的题目是「网络位置与学业表现」。一句话：我们想知道，一个学生在朋友网络里所处的位置，能不能预测他的成绩——而且是在「他的朋友都是谁」之外，额外还带的信息。

**English**
Hi everyone. Our project is called "Network Position and Academic Performance." In one sentence: we want to know whether where a student sits in a friendship network predicts their grades — over and above who their direct friends are.

---

## Slide 2 — 谜题 / The puzzle  ·  ~55 s  ·  讲者 A

**中文**
先看一个场景。左边这个学生，很多人直接给他点赞，但都集中在一个抱团的小圈子里。右边这个，直接点赞他的人少一些，可是通过朋友的朋友，他连到了学校里很多松散的群体。
假设这两个人的朋友数量一样、朋友的平均成绩也一样。那他们的成绩，应该一样吗？
我们的研究问题就是这一句：学生在朋友网络里的位置，会不会影响他的成绩？

**English**
Here's a scenario. The student on the left gets a lot of direct likes, but all inside one tight-knit circle. The student on the right gets fewer direct likes, but through friends of friends he reaches many loosely connected groups across the school.
Suppose these two have the same number of friends and the same average friend GPA. Should we expect them to end up with the same grades?
That's our research question: does a student's position in a friendship network affect their grades?

---

## Slide 3 — 前人的空白 / Prior work, and the gap  ·  ~70 s  ·  讲者 A

**中文**
这个方向最有名的研究是 Smirnov 和 Thurner 2017 年的论文。他们拿到一份真实的、随时间变化的俄罗斯学生「谁给谁点赞」网络，配上成绩。
他们的发现是：朋友之间成绩相似，主要来自选择——学生会去挑成绩跟自己差不多的人做朋友，而不是被朋友的成绩带高或带低。
但他们衡量一个学生，只用一个数字：这个学生直接朋友的平均成绩。
这里有个空白：他们从来不问，这个学生在整张网络里坐在什么位置。两个直接朋友相同的人，在他们的方法里得分完全一样——哪怕这两个人背后的社交世界差得很远。这个空白就是我们要补的。

**English**
The best-known study here is Smirnov and Thurner, 2017. They had a real, changing "who-likes-who" network of Russian students, matched to GPA.
What they found: the fact that friends have similar grades is mostly selection — students choose friends whose GPA is close to their own, rather than being pulled up or down by their friends' grades.
But they summarise each student with a single number: the average GPA of that student's direct friends.
Here's the gap: they never ask where that student sits in the wider network. Two students with the same direct friends get the same score in their method — no matter how different those friends' own social worlds are. That gap is what we fill.

---

## Slide 4 — 模型 / The model  ·  ~70 s  ·  讲者 B

**中文**
要谈「位置」，我们需要一个模型。这个模型来自 Zenou 等人——也就是我们这门课的老师之一。
设定很简单：每个学生 i 选一个学习努力 x_i，他的收益有三块。
第一块 a·x_i，是学习本身的好处。第二块 −½·x_i²，是成本——一个人闷头学，边际收益递减。
第三块是关键，是社交的部分：φ 乘以「你的努力 × 朋友的努力」。意思是，当你的朋友学得更努力，你自己多学一点的回报也会变高。φ 大于零，就是这种带动效应的强度。

**English**
To talk about "position," we need a model. This one is from Zenou and coauthors — and Zenou is one of the lecturers for this course.
The setup is simple. Each student i chooses a study effort x_i, and their payoff has three parts.
The first part, a times x_i, is the benefit of studying. The second, minus one-half x_i squared, is the cost — studying alone has diminishing returns.
The third part is the key one, and it's social: phi, times your effort, times a friend's effort. It means when your friends study harder, your own return to studying goes up too. Phi, greater than zero, is the strength of that spillover.

---

## Slide 5 — 均衡 / The equilibrium  ·  ~75 s  ·  讲者 B

**中文**
对每个学生求最优，得到最优反应：学一个基础量，再加上——你朋友学得越多，你也学得越多。
让全班同时都做最优选择，解出来这个式子。结论是：每个人的努力，正比于他的 Katz-Bonacich 中心性。
Katz-Bonacich 中心性数的是：你通过各种长度的路径能够到多少人，越远的路径打的折扣越大。
这个预测很硬、也很好证伪：成绩应该跟着这一个指标走——不是跟着「有多少人喜欢你」，也不是别的网络指标。φ 是模型自带的参数，也正是我们在数据里要调的东西。在原论文用美国数据做的检验里，中心性高一个标准差，成绩高大约百分之七个标准差。

**English**
Optimising for each student gives the best response: study a baseline amount, plus more when your friends study more.
Now let the whole class optimise at the same time, and solve. The result is: each student's effort is proportional to their Katz–Bonacich centrality.
Katz–Bonacich centrality counts how many people you can reach through paths of every length, discounting longer paths more.
This is a sharp, falsifiable prediction: achievement should track this one measure — not "how many people like you," not any other network measure. Phi is the model's own parameter, and it's exactly the thing we vary in the data. In the original study, on US data, a one-standard-deviation rise in centrality raised school performance by about seven percent of a standard deviation.

---

## Slide 6 — φ 旋钮 / The dial  ·  ~70 s  ·  讲者 B

**中文**
这张图是整个项目最核心的直觉。φ 是一个旋钮。
旋到最左边，φ 趋近零：这个指标基本只数你的直接朋友，等于「人气」，也就是入度。
旋到最右边，φ 趋近它的上限：长的、绕圈子的路径几乎和短路径一样重要，这个指标衡量的是「你在整张网里的位置」——是不是连接不同群体的桥梁。
所以同一个公式，旋钮一转，它测的东西就从「你有多少朋友」变成「你在网络的什么位置」。我们会在六个 φ 值上都算一遍，看在哪一段，它能预测成绩。

**English**
This picture is the core intuition of the whole project. Phi is a dial.
Turn it all the way left, phi near zero: the measure basically just counts your direct friends — it's popularity, in-degree.
Turn it all the way right, phi near its ceiling: long, indirect paths matter almost as much as short ones, and the measure now captures where you sit in the whole network — whether you're a bridge between separate groups.
So it's the same formula, but as you turn the dial it stops measuring "how many friends" and starts measuring "where in the network." We compute it at six values of phi and see where, along the dial, it predicts GPA.

---

## Slide 7 — 预测 / Predictions  ·  ~70 s  ·  讲者 C

**中文**
分三组。
来自模型的主预测：控制了「朋友平均成绩」和「原始人气」之后，Katz-Bonacich 中心性仍然能预测下一学期的成绩。如果加进原始人气它就不显著了，或者它沿着 φ 旋钮变号，那模型这个说法在这份数据上就是被推翻了。
如果它真能预测，方向是哪个：正号——位置带来的信息和帮助抬高成绩；零——好处和时间成本抵消；负号——铺得太广，占用了学习时间。
复现 Smirnov 和 Thurner：朋友过去的成绩预测不了你未来的成绩；新交的朋友成绩差距比断掉的朋友小，这是选择的信号；选择效应在大学比中学更强。

**English**
Three groups of predictions.
The main one, from the model: even after we control for average friend GPA and for raw popularity, Katz–Bonacich centrality still predicts next-term GPA. It's falsified if it goes insignificant once degree is in, or if it flips sign along the phi dial.
If it does predict — which direction? Positive: the information and help that come with position raise grades. Zero: the benefits and the time costs cancel. Negative: reaching too widely eats into study time.
And replicating Smirnov and Thurner: a friend's past GPA won't predict your future GPA; new friendships have a smaller GPA gap than ones that end, which is the signature of selection; and selection is stronger at university than in high school.

---

## Slide 8 — 数据 / The data  ·  ~55 s  ·  讲者 C

**中文**
数据是真实的有向网络。节点是学生——中学 655 人，大学每个年级一千二到一千五。
边是「点赞」，有方向：i 指向 j 表示 i 在三个月里至少给 j 点过一次赞。每个组有 2 到 14 个时间快照，一共 38 个。只有四分之一左右是互相点赞。
属性有成绩，以及各种网络指标。
关键一点：这就是 Smirnov 和 Thurner 用的同一份数据，所以我们的结果可以跟他们直接对比。

**English**
The data is a real, directed network. Nodes are students — 655 in high school, and twelve hundred to fifteen hundred per university year.
Edges are "likes," and they have direction: i to j means i liked j at least once within a three-month window. There are between 2 and 14 snapshots per group, 38 in total. Only about a quarter of the ties are mutual.
Attributes are GPA plus the network measures.
The key point: this is the same dataset Smirnov and Thurner used, so our results compare directly with theirs.

---

## Slide 9 — 回归方法 / How we estimate it  ·  ~65 s  ·  讲者 C

**中文**
我们的做法：用这学期的网络位置，预测下学期的成绩，同时控制住其他东西。
每个控制项都有明确任务。控制「朋友平均成绩」——这是 Smirnov 和 Thurner 自己的变量——所以我们的系数是剔除了朋友圈构成之后的。控制「原始的点赞数」——所以系数是剔除了人气之后的。
于是真正的问题是：中心性，在「单纯数朋友个数」之外，还带不带额外的信息？

**English**
Our approach: use this term's network position to predict next term's GPA, while holding the rest fixed.
Each control does a specific job. We control for average friend GPA — that's Smirnov and Thurner's own variable — so our coefficient is net of friend-group composition. We control for the raw like counts — so it's also net of popularity.
Which leaves the real question: does centrality carry anything beyond simply counting friends?

---

## Slide 10 — 箭头往哪走 / Which way the arrow runs  ·  ~65 s  ·  讲者 D

**中文**
有人会问：到底是位置抬高了成绩，还是成绩好的人本来就招朋友？单个时间点的数据分不清。我们的面板数据在三个地方帮上忙。
第一，时间顺序：位置测在前，成绩看在后。
第二，控制过去的成绩：我们只比「当前成绩相同」的学生。
第三，直接量反向那条箭头：成绩上升会不会带来新朋友——这正是 Smirnov 和 Thurner 那套建关系、断关系的方法。
我们诚实的说法是：位置能预测后面的成绩，不是位置导致成绩。

**English**
Someone will ask: does position raise grades, or do students with good grades just attract more friends? A single snapshot can't tell them apart. Our panel data helps in three ways.
One, time order: position is measured before the GPA it predicts.
Two, we control for past GPA: we only compare students who currently have the same grade.
Three, we measure the reverse arrow directly: does a rise in GPA bring new friends? That's exactly Smirnov and Thurner's method of tracking ties forming and breaking.
Our honest claim is that position predicts later grades — not that it causes them.

---

## Slide 11 — 计划 / The plan  ·  ~55 s  ·  讲者 D

**中文**
三层。第一层，复现——在同一份数据上重跑 Smirnov 和 Thurner 的检验。第二层，检验模型——算 Katz-Bonacich 中心性，沿整个 φ 旋钮测它的预测。第三层，比较——中学对大学，看效应是不是随场景变化。
一个细节：我们的主检验参数在跑之前就定死，φ 取上限的百分之八十五，这样后面的稳健性检查不会被说成「挑好看的结果」。

**English**
Three layers. Layer one, replicate — re-run Smirnov and Thurner's checks on the same data. Layer two, test the model — compute Katz–Bonacich centrality and test its prediction across the whole phi dial. Layer three, compare — high school versus university, to see whether the effect holds across settings.
One detail: our main test is pre-registered — we fix phi at eighty-five percent of its ceiling before running anything — so the later robustness checks can't be accused of cherry-picking.

---

## Slide 12 — 提问 / Questions  ·  ~15 s  ·  讲者 D

**中文**
数据和模型的出处在这里，更详细的写在我们的 research brief 里。谢谢，欢迎提问。

**English**
The sources for the data and the model are here, and the full detail is in our research brief. Thank you — happy to take questions.

---

## 3 人分工 / 3-speaker split

- 讲者 1：Slide 1–4（开场谜题 → 研究问题 → S&T 的空白 → 模型设定）
- 讲者 2：Slide 5–8（均衡 = Katz-Bonacich → φ 旋钮 → 我们的预测 → 数据）
- 讲者 3：Slide 9–12（回归方法 → 箭头往哪走 → 三层计划 → 收尾提问）

## 超时时怎么砍 / If running long

- Slide 7：预测三组只讲「来自模型的主预测」。
- Slide 11：计划一句话带过，重点留一句「预注册」。
- Slide 5：跳过 7% 那个数字。
