import copy
from random import choice
from Initialization import *


class DiffusionNormalIC:
    def __init__(self, g_dict, s_c_dict, prod_list, pps, wpiwp):
        ### g_dict: (dict) the graph
        ### s_c_dict: (dict) the set of cost for seeds
        ### prod_list: (list) the set to record products [kk's profit, kk's cost, kk's price]
        ### num_node: (int) the number of nodes
        ### num_product: (int) the kinds of products
        ### pp_strategy: (int) the strategy to update personal prob.
        ### wpiwp: (bool) whether passing the information without purchasing
        self.graph_dict = g_dict
        self.seed_cost_dict = s_c_dict
        self.product_list = prod_list
        self.num_node = len(s_c_dict)
        self.num_product = len(prod_list)
        self.pps = pps
        self.wpiwp = wpiwp

    def setPersonalProbList(self, w_list):
        # -- according to pps, initialize the pp_list --
        # -- if the node i can't purchase the product k, then pp_list[k][i] = 0 --
        ### pp_list: (list) the list of personal prob. for all combinations of nodes and products
        ### pp_list[k]: (list) the list of personal prob. for k-product
        ### pp_list[k][i]: (float2) the personal prob. for i-node for k-product
        pp_list = [[1.0 for _ in range(self.num_node)] for _ in range(self.num_product)]

        for k in range(self.num_product):
            for i in range(self.num_node):
                if w_list[i] < self.product_list[k][2]:
                    pp_list[k][i] = 0

        for k in range(self.num_product):
            prod_price = self.product_list[k][2]
            for i in self.seed_cost_dict:
                if pp_list[k][int(i)] != 0:
                    if self.pps == 1:
                        # -- after buying a product, the prob. to buy another product will decrease randomly --
                        pp_list[k][int(i)] = round(random.uniform(0, pp_list[k][int(i)]), 4)
                    elif self.pps == 2:
                        # -- choose as expensive as possible --
                        pp_list[k][int(i)] *= round((prod_price / w_list[int(i)]), 4)
                    elif self.pps == 3:
                        # -- choose as cheap as possible --
                        pp_list[k][int(i)] *= round(1 - (prod_price / w_list[int(i)]), 4)

        return pp_list

    def updatePersonalProbList(self, k_prod, i_node, w_list, pp_list):
        prod_price = self.product_list[k_prod][2]
        if self.pps == 1:
            # -- after buying a product, the prob. to buy another product will decrease randomly --
            for k in range(self.num_product):
                if k == k_prod:
                    pp_list[k][int(i_node)] = 0
                else:
                    pp_list[k][int(i_node)] = round(random.uniform(0, pp_list[k][int(i_node)]), 4)
        elif self.pps == 2:
            # -- choose as expensive as possible --
            for k in range(self.num_product):
                if k == k_prod:
                    pp_list[k][int(i_node)] = 0
                else:
                    pp_list[k][int(i_node)] *= round((prod_price / w_list[int(i_node)]), 4)
        elif self.pps == 3:
            # -- choose as cheap as possible --
            for k in range(self.num_product):
                if k == k_prod:
                    pp_list[k][int(i_node)] = 0
                else:
                    pp_list[k][int(i_node)] *= round(1 - (prod_price / w_list[int(i_node)]), 4)

        for k in range(self.num_product):
            for i in range(self.num_node):
                if w_list[i] < self.product_list[k][2]:
                    pp_list[k][i] = 0.0

        return pp_list

    def getPersonalProbClassList(self, pp_list):
        c = [[0 for _ in range(11)] for _ in range(self.num_product)]
        for k in range(self.num_product):
            for i in range(self.num_node):
                c[k][int(pp_list[k][i] * 10)] += 1

        return c

    def getSeedSetProfit(self, k_prod, i_node, s_set, w_list, pp_list):
        # -- calculate the expected profit for single node when it's chosen as a seed --
        ### try_a_n_list: (list) the set to store the nodes may be activated for kk-products
        ### try_a_n_list[][0]: (str) the receiver when ii is ancestor
        ### try_a_n_list[][1]: (float2) the probability to activate the receiver from ii
        ### try_a_n_list[][2]: (float2) the personal probability to activate own self
        ### ep: (float2) the expected profit
        s_total_set = set()
        s_set_t = copy.deepcopy(s_set)
        s_set_t[k_prod].add(i_node)
        for k in range(self.num_product):
            s_total_set = s_total_set.union(s_set_t[k])
        a_n_set = copy.deepcopy(s_set_t)
        a_e_set = [{} for _ in range(self.num_product)]
        ep = 0.0

        # -- add the receivers of nnode into try_a_n_list --
        # -- notice: prevent the node from owing no receiver --
        if i_node not in self.graph_dict:
            return ep

        try_s_n_sequence, try_a_n_sequence = [], []
        for k in range(self.num_product):
            for i in s_set_t[k]:
                try_s_n_sequence.append([k, i])

        while len(try_s_n_sequence) > 0:
            seed = choice(try_s_n_sequence)
            try_s_n_sequence.remove(seed)
            k_prod_t, i_node_t = seed[0], seed[1]

            out_dict = self.graph_dict[i_node_t]
            for out in out_dict:
                if not (out not in a_n_set[k_prod_t]):
                    continue
                if not (out not in s_total_set):
                    continue
                if not (i_node not in a_e_set[k_prod_t] or out not in a_e_set[k_prod_t][i_node]):
                    continue
                if not (w_list[int(out)] > self.product_list[k_prod_t][2]):
                    continue
                if not (pp_list[k_prod_t][int(out)] > 0):
                    continue
                # -- add the value calculated by activated probability * profit of this product --
                od = float(out_dict[out])
                temp_ep = od * pp_list[k_prod_t][int(out)] * self.product_list[k_prod][0]
                # if str(round(ep, 3)) != str(round(ep + temp_ep, 3)):
                ep += temp_ep
                # -- activate the receivers temporally --
                # -- add the receiver of node into try_a_n_list --
                # -- notice: prevent the node from owing no receiver --
                try_a_n_sequence.append([k_prod_t, out, od, od, 1])
                a_n_set[k_prod_t].add(i_node_t)
                if i_node_t in a_e_set[k_prod_t]:
                    a_e_set[k_prod_t][i_node_t].add(out)
                else:
                    a_e_set[k_prod_t][i_node_t] = {out}

        while len(try_a_n_sequence) > 0:
            ### try_node: (list) the nodes may be activated for kk-products
            try_node = choice(try_a_n_sequence)
            try_a_n_sequence.remove(try_node)
            k_prod_t, i_node_t, i_prob_t, i_acc_prob_t = try_node[0], try_node[1], try_node[2], try_node[3]
            ddd = try_node[4]

            if i_node_t not in self.graph_dict:
                continue

            out_dict = self.graph_dict[i_node_t]
            for out in out_dict:
                if not (out not in a_n_set[k_prod_t]):
                    continue
                if not (out not in s_total_set):
                    continue
                if not (i_node not in a_e_set[k_prod_t] or out not in a_e_set[k_prod_t][i_node]):
                    continue
                if not (w_list[int(out)] > self.product_list[k_prod][2]):
                    continue
                if not (pp_list[k_prod_t][int(out)] > 0):
                    continue
                # -- add the value calculated by activated probability * profit of this product --
                od = float(out_dict[out])
                temp_ep = i_acc_prob_t * pp_list[k_prod_t][int(out)] * self.product_list[k_prod][0]

                # if str(round(ep, 3)) != str(round(ep + temp_ep, 3)):
                if ddd >= 3:
                    ep += temp_ep

                    try_a_n_sequence.append([k_prod_t, out, od, round(i_prob_t * od, 2), ddd + 1])
                    a_n_set[k_prod_t].add(i_node_t)
                    if i_node_t in a_e_set[k_prod_t]:
                        a_e_set[k_prod_t][i_node_t].add(out)
                    else:
                        a_e_set[k_prod_t][i_node_t] = {out}
        # print(round(ep, 2))
        return round(ep, 2)

    # def getSeedSetProfit(self, k_prod, i_node, s_set, w_list, pp_list):
    #     # -- calculate the expected profit for single node when i_node's chosen as a seed for k-product --
    #     monte = 100
    #     ### ep: (float4) the expected profit
    #     s_total_set = set()
    #     s_set_t = copy.deepcopy(s_set)
    #     s_set_t[k_prod].add(i_node)
    #     for k in range(self.num_product):
    #         s_total_set = s_total_set.union(s_set_t[k])
    #     purc_set = [set() for _ in range(self.num_product)]
    #     a_n_set = copy.deepcopy(s_set_t)
    #     a_e_set = [{} for _ in range(self.num_product)]
    #     ep = 0.0
    #
    #     pro_k_list, pnn_k_list = [0.0 for _ in range(self.num_product)], [0 for _ in range(self.num_product)]
    #
    #     # -- notice: prevent the node from owing no receiver --
    #     if i_node not in self.graph_dict:
    #         return round(ep, 4), pro_k_list, pnn_k_list
    #
    #     for _ in range(monte):
    #         # -- insert the children of seeds into try_s_n_sequence --
    #         ### try_s_n_sequence: (list) the sequence to store the seed for k-products [k, i]
    #         ### try_a_n_sequence: (list) the sequence to store the nodes may be activated for k-products [k, i, prob]
    #         try_s_n_sequence, try_a_n_sequence = [], []
    #         for k in range(self.num_product):
    #             for i in s_set_t[k]:
    #                 try_s_n_sequence.append([k, i])
    #
    #         while len(try_s_n_sequence) > 0:
    #             seed = choice(try_s_n_sequence)
    #             try_s_n_sequence.remove(seed)
    #             k_prod_t, i_node_t = seed[0], seed[1]
    #
    #             if i_node_t not in self.graph_dict:
    #                 continue
    #
    #             out_dict = self.graph_dict[i_node_t]
    #             for out in out_dict:
    #                 if out in s_total_set:
    #                     continue
    #                 if out in a_n_set[k_prod_t]:
    #                     continue
    #                 if i_node_t in a_e_set[k_prod_t] and out in a_e_set[k_prod_t][i_node_t]:
    #                     continue
    #                 p = pp_list[k_prod_t][int(out)]
    #                 if p == 0:
    #                     continue
    #                 r = random.random()
    #                 od = float(out_dict[out])
    #                 if r < od:
    #                     try_a_n_sequence.append([k_prod_t, out, self.graph_dict[i_node_t][out]])
    #                     a_n_set[k_prod_t].add(out)
    #                     if i_node_t in a_e_set[k_prod_t]:
    #                         a_e_set[k_prod_t][i_node_t].add(out)
    #                     else:
    #                         a_e_set[k_prod_t][i_node_t] = {out}
    #
    #             # -- activate the nodes --
    #             dnic_d = DiffusionNormalIC(self.graph_dict, self.seed_cost_dict, self.product_list, self.pps, self.wpiwp)
    #
    #             while len(try_a_n_sequence) > 0:
    #                 try_node = choice(try_a_n_sequence)
    #                 try_a_n_sequence.remove(try_node)
    #                 k_prod_t, i_node_t, i_prob_t = try_node[0], try_node[1], try_node[2]
    #                 dp = bool(0)
    #
    #                 ### -- whether purchasing or not --
    #                 r = random.random()
    #                 p = pp_list[k_prod_t][int(i_node_t)]
    #                 if r < p:
    #                     purc_set[k_prod_t].add(i_node_t)
    #                     a_n_set[k_prod_t].add(i_node_t)
    #                     w_list[int(i_node_t)] -= self.product_list[k_prod_t][2]
    #                     pp_list = dnic_d.updatePersonalProbList(k_prod_t, i_node_t, w_list, pp_list)
    #                     ep += self.product_list[k_prod_t][0]
    #                     dp = bool(1)
    #
    #                     pro_k_list[k_prod_t] += self.product_list[k_prod_t][0]
    #
    #                 if i_node_t not in self.graph_dict:
    #                     continue
    #
    #                 ### -- whether passing the information or not --
    #                 if self.wpiwp or dp:
    #                     out_dict = self.graph_dict[i_node_t]
    #                     for out in out_dict:
    #                         if out in s_total_set:
    #                             continue
    #                         if out in a_n_set[k_prod_t]:
    #                             continue
    #                         if i_node_t in a_e_set[k_prod_t] and out in a_e_set[k_prod_t][i_node_t]:
    #                             continue
    #                         if pp_list[k_prod_t][int(out)] == 0:
    #                             continue
    #                         r = random.random()
    #                         od = float(out_dict[out])
    #                         if r < od:
    #                             try_a_n_sequence.append([k_prod_t, out, self.graph_dict[i_node_t][out]])
    #                             a_n_set[k_prod_t].add(i_node_t)
    #                             if i_node_t in a_e_set[k_prod_t]:
    #                                 a_e_set[k_prod_t][i_node_t].add(out)
    #                             else:
    #                                 a_e_set[k_prod_t][i_node_t] = {out}
    #
    #     for k in range(self.num_product):
    #         pro_k_list[k] = round(pro_k_list[k] / monte, 4)
    #         pnn_k_list[k] = round(len(purc_set[k]) / monte, 4)
    #
    #     return round(ep / monte, 4), pro_k_list, pnn_k_list


class Evaluation:
    def __init__(self, g_dict, s_c_dict, prod_list, pps, wpiwp):
        ### g_dict: (dict) the graph
        ### s_c_dict: (dict) the set of cost for seeds
        ### prod_list: (list) the set to record products [kk's profit, kk's cost, kk's price]
        ### num_node: (int) the number of nodes
        ### num_product: (int) the kinds of products
        ### pp_strategy: (int) the strategy to update personal prob.
        ### wpiwp: (bool) whether passing the information without purchasing
        self.graph_dict = g_dict
        self.seed_cost_dict = s_c_dict
        self.product_list = prod_list
        self.num_node = len(s_c_dict)
        self.num_product = len(prod_list)
        self.pps = pps
        self.wpiwp = wpiwp

    def getSeedSetProfit(self, s_set, w_list, pp_list):
        # -- calculate the expected profit for single node when i_node's chosen as a seed for k-product --
        ### ep: (float4) the expected profit
        s_total_set = set()
        for k in range(self.num_product):
            s_total_set = s_total_set.union(s_set[k])
        purc_set = [set() for _ in range(self.num_product)]
        a_n_set = copy.deepcopy(s_set)
        a_e_set = [{} for _ in range(self.num_product)]
        ep = 0.0

        pro_k_list, pnn_k_list = [0.0 for _ in range(self.num_product)], [0 for _ in range(self.num_product)]

        # -- insert the children of seeds into try_s_n_sequence --
        ### try_s_n_sequence: (list) the sequence to store the seed for k-products [k, i]
        ### try_a_n_sequence: (list) the sequence to store the nodes may be activated for k-products [k, i, prob]
        try_s_n_sequence, try_a_n_sequence = [], []
        for k in range(self.num_product):
            for i in s_set[k]:
                try_s_n_sequence.append([k, i])

        while len(try_s_n_sequence) > 0:
            seed = choice(try_s_n_sequence)
            try_s_n_sequence.remove(seed)
            k_prod_t, i_node_t = seed[0], seed[1]

            if i_node_t not in self.graph_dict:
                continue

            out_dict = self.graph_dict[i_node_t]
            for out in out_dict:
                if out in s_total_set:
                    continue
                if out in a_n_set[k_prod_t]:
                    continue
                if i_node_t in a_e_set[k_prod_t] and out in a_e_set[k_prod_t][i_node_t]:
                    continue
                if pp_list[k_prod_t][int(out)] == 0:
                    continue
                if random.random() <= float(out_dict[out]):
                    try_a_n_sequence.append([k_prod_t, out, self.graph_dict[i_node_t][out]])
                    a_n_set[k_prod_t].add(i_node_t)
                    if i_node_t in a_e_set[k_prod_t]:
                        a_e_set[k_prod_t][i_node_t].add(out)
                    else:
                        a_e_set[k_prod_t][i_node_t] = {out}

            # -- activate the nodes --
            dnic_d = DiffusionNormalIC(self.graph_dict, self.seed_cost_dict, self.product_list, self.pps, self.wpiwp)

            while len(try_a_n_sequence) > 0:
                try_node = choice(try_a_n_sequence)
                try_a_n_sequence.remove(try_node)
                k_prod_t, i_node_t, i_prob_t = try_node[0], try_node[1], try_node[2]
                dp = bool(0)

                ### -- whether purchasing or not --
                if random.random() <= pp_list[k_prod_t][int(i_node_t)]:
                    purc_set[k_prod_t].add(i_node_t)
                    a_n_set[k_prod_t].add(i_node_t)
                    w_list[int(i_node_t)] -= self.product_list[k_prod_t][2]
                    pp_list = dnic_d.updatePersonalProbList(k_prod_t, i_node_t, w_list, pp_list)
                    ep += self.product_list[k_prod_t][0]
                    dp = bool(1)

                    pro_k_list[k_prod_t] += self.product_list[k_prod_t][0]

                if i_node_t not in self.graph_dict:
                    continue

                ### -- whether passing the information or not --
                if self.wpiwp or dp:
                    out_dict = self.graph_dict[i_node_t]
                    for out in out_dict:
                        if out in s_total_set:
                            continue
                        if out in a_n_set[k_prod_t]:
                            continue
                        if i_node_t in a_e_set[k_prod_t] and out in a_e_set[k_prod_t][i_node_t]:
                            continue
                        if pp_list[k_prod_t][int(out)] == 0:
                            continue
                        if random.random() <= float(out_dict[out]):
                            try_a_n_sequence.append([k_prod_t, out, self.graph_dict[i_node_t][out]])
                            a_n_set[k_prod_t].add(i_node_t)
                            if i_node_t in a_e_set[k_prod_t]:
                                a_e_set[k_prod_t][i_node_t].add(out)
                            else:
                                a_e_set[k_prod_t][i_node_t] = {out}

        for k in range(self.num_product):
            pro_k_list[k] = round(pro_k_list[k], 4)
            pnn_k_list[k] = round(len(purc_set[k]), 4)

        return round(ep, 4), pro_k_list, pnn_k_list