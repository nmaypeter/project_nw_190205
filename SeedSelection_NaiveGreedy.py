from Diffusion_NormalIC import *


class SeedSelectionNG:
    def __init__(self, g_dict, s_c_dict, prod_list, total_bud, pps, wpiwp):
        ### g_dict: (dict) the graph
        ### s_c_dict: (dict) the set of cost for seeds
        ### prod_list: (list) the set to record products [kk's profit, kk's cost, kk's price]
        ### total_bud: (int) the budget to select seed
        ### num_node: (int) the number of nodes
        ### num_product: (int) the kinds of products
        ### pps: (int) the strategy to update personal prob.
        ### wpiwp: (bool) whether passing the information without purchasing
        self.graph_dict = g_dict
        self.seed_cost_dict = s_c_dict
        self.product_list = prod_list
        self.total_budget = total_bud
        self.num_node = len(s_c_dict)
        self.num_product = len(prod_list)
        self.pps = pps
        self.wpiwp = wpiwp

    def getMostValuableSeed(self, s_set, nban_set, cur_bud, w_list, pp_list):
        # -- calculate expected profit for all combinations of nodes and products --
        ### ban_set: (list) the set to record the node that will be banned
        ### mep: (list) [#product, #node, expected profit, profit per product, purchasing node number per product]
        ban_set = [set() for _ in range(self.num_product)]
        mep = [0, '-1', 0.0]
        # mep = [0, '-1', 0.0, [0.0 for _ in range(self.num_product)], [0 for _ in range(self.num_product)]]
        dnic_s = DiffusionNormalIC(self.graph_dict, self.seed_cost_dict, self.product_list, self.pps, self.wpiwp)
        a, b, c = 0, 0, 0
        mt = 0
        st = 0

        for k in range(self.num_product):
            # lll = len(nban_set[k])
            for i in nban_set[k]:
                # lll -= 1
                # print(k, lll)
                # -- the cost of seed cannot exceed the budget --
                if self.seed_cost_dict[i] + cur_bud > self.total_budget:
                    a += 1
                    ban_set[k].add(i)
                    continue
                ep, t = dnic_s.getSeedSetProfit(k, i, s_set, copy.deepcopy(w_list), copy.deepcopy(pp_list))
                mt = max(mt, t)
                st += t
                # ep, pro_k_list, pnn_k_list = dnic_s.getSeedSetProfit(k, i, s_set, copy.deepcopy(w_list), copy.deepcopy(pp_list))
                bud_ep = cur_bud + self.seed_cost_dict[i]
                if mep[1] == '-1':
                    bud_mep = cur_bud
                else:
                    bud_mep = cur_bud + self.seed_cost_dict[mep[1]]

                # -- the expected profit cannot be negative --
                if ep <= 0:
                    b += 1
                    ban_set[k].add(i)
                    continue

                # -- the expected profit cannot be negative --
                if t <= mt * 0.1:
                    c += 1
                    ban_set[k].add(i)
                    continue

                # -- choose the better seed --
                if ep > mep[2]:
                # if ep - bud_ep > mep[2] - bud_mep or bud_mep == 0.0:
                #     mep = [k, i, ep, pro_k_list, pnn_k_list]
                    mep = [k, i, ep]
        print('a, b, c')
        print(a, b, c)
        print('st')
        print(st)

        # -- remove the impossible seeds from nban_set
        print('nban')
        for k in range(self.num_product):
            for i in ban_set[k]:
                if i in nban_set[k]:
                    nban_set[k].remove(i)
            print(len(nban_set[k]))

        return mep, nban_set


if __name__ == "__main__":
    data_set_name = "email_undirected"
    product_name = "r1p3n1"
    total_budget = 8
    pp_strategy = 1
    whether_passing_information_without_purchasing = bool(0)

    iniG = IniGraph(data_set_name)
    iniP = IniProduct(product_name)

    seed_cost_dict = iniG.constructSeedCostDict()[1]
    graph_dict = iniG.constructGraphDict()
    product_list = iniP.getProductList()[0]
    wallet_list = iniG.getWalletList(product_name)
    num_node = len(seed_cost_dict)
    num_product = len(product_list)

    ssng = SeedSelectionNG(graph_dict, seed_cost_dict, product_list, total_budget, pp_strategy, whether_passing_information_without_purchasing)
    dnic = DiffusionNormalIC(graph_dict, seed_cost_dict, product_list, pp_strategy, whether_passing_information_without_purchasing)
    eva = Evaluation(graph_dict, seed_cost_dict, product_list, pp_strategy, whether_passing_information_without_purchasing)

    personal_prob_list = dnic.setPersonalProbList(wallet_list)

    # -- initialization for each budget --
    start_time = time.time()
    ### result: (list) [profit, budget, seed number per product, customer number per product, seed set] in this execution_time
    result = []
    avg_profit, avg_budget = 0.0, 0.0
    avg_num_k_seed, avg_num_k_pn = [0 for _ in range(num_product)], [0 for _ in range(num_product)]
    bud_k_list = [0.0 for _ in range(num_product)]

    # -- initialization for each sample_number --
    ### notban_seed_set: (list) the possible seed set
    ### notban_seed_set[kk]: (set) the possible seed set for kk-product
    notban_seed_set = [set(graph_dict.keys()) for _ in range(num_product)]
    ### now_profit, now_budget: (float) the profit and budget in this execution_time
    now_profit, now_budget = 0.0, 0.0
    ### seed_set: (list) the seed set
    ### seed_set[kk]: (set) the seed set for kk-product
    seed_set = [set() for _ in range(num_product)]

    print('time')
    print(round(time.time() - start_time, 2))
    print("getMostValuableSeed")
    temp = time.time()

    mep, nban_seed_set = ssng.getMostValuableSeed(seed_set, copy.deepcopy(notban_seed_set), now_budget, copy.deepcopy(wallet_list), copy.deepcopy(personal_prob_list))
    mep_k_prod, mep_i_node, mep_profit = mep[0], mep[1], mep[2]
    # mep_k_prod, mep_i_node, mep_profit, mep_pro_k_list, mep_pnn_k_list = mep[0], mep[1], mep[2], mep[3], mep[4]
    print(mep)

    # -- main --
    while now_profit < mep_profit and mep_i_node != '-1':
        print('time')
        print(round(time.time() - start_time, 2))
        print(round(time.time() - temp, 2))
        print("insertSeedIntoSeedSet")
        temp = time.time()
        for kk in range(num_product):
            if mep_i_node in nban_seed_set[kk]:
                nban_seed_set[kk].remove(mep_i_node)
        seed_set[mep_k_prod].add(mep_i_node)
        print('seed_set')
        print(seed_set)

        bud_k_list[mep_k_prod] += seed_cost_dict[mep_i_node]
        now_profit = mep_profit
        now_budget += seed_cost_dict[mep_i_node]
        print('bud_k_list, now_profit, now_budget')
        print(bud_k_list, now_profit, now_budget)
        # print('pro_k_list, bud_k_list, now_profit, now_budget')
        # print(mep_pro_k_list, bud_k_list, now_profit, now_budget)

        print('time')
        print(round(time.time() - start_time, 2))
        print(round(time.time() - temp, 2))
        print("getMostValuableSeed")
        mep, nban_seed_set = ssng.getMostValuableSeed(seed_set, nban_seed_set, now_budget, copy.deepcopy(wallet_list), copy.deepcopy(personal_prob_list))
        mep_k_prod, mep_i_node, mep_profit = mep[0], mep[1], mep[2]
        # mep_k_prod, mep_i_node, mep_profit, mep_pro_k_list, mep_pnn_k_list = mep[0], mep[1], mep[2], mep[3], mep[4]
        print('mep_profit, mep_i_node')
        print(mep_profit, mep_i_node)

    pro_acc, pro_k_list_acc, pnn_k_list_acc = 0.0, [0.0 for _ in range(num_product)], [0 for _ in range(num_product)]
    for _ in range(100):
        pro, pro_k_list, pnn_k_list = eva.getSeedSetProfit(seed_set, copy.deepcopy(wallet_list), copy.deepcopy(personal_prob_list))
        pro_acc += pro
        for kk in range(num_product):
            pro_k_list_acc[kk] += pro_k_list[kk]
            pnn_k_list_acc[kk] += pnn_k_list[kk]
    pro_acc = round(pro_acc / 100, 2)
    for kk in range(num_product):
        pro_k_list_acc[kk] = round(pro_k_list_acc[kk] / 100, 2)
        pnn_k_list_acc[kk] = round(pnn_k_list_acc[kk] / 100, 2)
    now_budget = round(now_budget, 2)

    # -- result --
    now_num_k_seed = [len(kk) for kk in seed_set]
    result.append([pro_acc, now_budget, now_num_k_seed, pnn_k_list_acc, seed_set])
    avg_profit += now_profit
    avg_budget += now_budget
    for kk in range(num_product):
        avg_num_k_seed[kk] += now_num_k_seed[kk]
        avg_num_k_pn[kk] += pnn_k_list_acc[kk]
    how_long = round(time.time() - start_time, 2)
    print("result")
    print(result)
    print("\npro_k_list, bud_k_list")
    print(pro_k_list_acc, bud_k_list)
    print("total time: " + str(how_long) + "sec")
