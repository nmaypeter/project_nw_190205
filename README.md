# project_nw_190205

2/8
1. setPersonalProbList一步到好，不用再額外替此步驟加工。
2. 引入monde carlo。
3. 為了能在影響過的node set中找到seed也不會計算誤差，將getSeedSetProfit使用為以seed set進行計算，以找出最大獲利的seed。也因此無法在main找出a_n_set及a_e_set，故在每次monde再實時計算。
4. SeedSelection_NaiveGreedy中廢除expect_profit_list，取而代之，直接找出mep。
5. while中原先以budget作為限制條件，但是新寫法預先剔除會超過budget的seed，因此不須使用budget限制。另外若是選擇仍在budget內反而會使得profit降低的seed，不應該出現如此情形，故將profit做為限制。

2/13
1. 不使用monde carlo，回復使用期望值來計算各seed set的ep，但是計算時間過久，光是找出一個seed就需要約100sec。
1.1 使用忽略過小值，若影響到的node加上的ep四捨五入至小術後第2位則捨去: 最便宜商品的價值完全被抹滅掉。
1.2 使用忽略過小值，若影響到的node加上的ep四捨五入至小術後第3位則捨去: 時間無法忍受。
1.3 使用一個dict來存放每一個seed的ep，當後來使用的seed有用到已存放的seed時，可以直接用累積機率乘起來相加: 前提為DAG才可使用。
1.4 使用傳遞的距離限制，只計算到影響層數3以內: 數值與時間可以接受，但是目前問題為得出ep時若考慮budget會盡量考慮小budget(因為ep實在太小)，而目前暫且不考慮budget。