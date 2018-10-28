# -*- coding: utf-8 -*-
import json
import random
from copy import deepcopy

import os

import requests
import bs4
import sqlite3

__author__ = "Jianyang Tang"
__email__ = "jian4yang2.tang1@gmail.com"


class Tile:
    """
        --------------------------------------------------------------------------------------------------------------
        The intentions of using this class:

            As you should have already known, when you decide to develop an AI agent of Mahjong, there are 34 kinds of
            different Mahjong tiles, i.e. 1-9 man, 1-9 pin, 1-9 suo, 7 character tiles(ESWNBFC). Another fact is that
            for each kind of tiles we have four identical copies, this makes a total of 136 tiles.

            Tiles are however represented in quite different ways for different situaions.

            For example, in the server for real-time human-to-human battling, tiles are represented in 136-form. By
            applying 136-form, each copy of a kind of tile is even identified with an ID. E.g.
                0,1,2,3 <=> the four 1 man tiles
                16,17,18,19 <=> the four 5 man tiles

            In the game log, where one can crawl from the tenhou.net, they use a more compact, yet not the most
            efficient way to represent tiles. The projection from tiles to its representation is as follows:
                11-19 <=> 1-9 man
                21-29 <=> 1-9 pin
                31-39 <=> 1-9 suo
                41-47 <=> ESWNBFC
                51,52,53 <=> red 5 man, pin, suo

            For developing your AI agent for Japanese Riichi Mahjong, we suggest to use the most compact 34-form. The
            mapping rule is quite easy:
                0-8 <=> 1-9 man
                9-17 <=> 1-9 pin
                18-26 <=> 1-9 suo
                27-33 <=> ESWNBFC
                34,35,36 <=> red 5 man,pin,suo

            So this class provides different class methods and attributes for converting between these three different
            representation systems.
        --------------------------------------------------------------------------------------------------------------
        Class attributes (Explanation):
            <-- TYPE: list of list ------------------------------------------>
            index_to_chow     id --> the tiles which make a chow in 34-form
            <-- TYPE: dictionary -------------------------------------------->
            his_to_34_dic     tiles in game history form --> 34-form
            bns_ind_bd_dic    bonus indicating tiles at border --> corresponding bonus tiles
            <-- TYPE: list -------------------------------------------------->
            to_graph_list     34-form --> unicode graph form
            tile_desc_list    34-form --> string from description
            WINDS             all wind tiles in 34-form
            THREES            all dragon tiles in 34-form
            HONORS            all character tiles in 34-form
            ONES              all tiles with number 1 in 34-form
            NINES             all tiles with number 9 in 34-form
            TERMINALS         all tiles either with number 1 or number 9 in 34-form
            ONENINE           terminal tiles plus character tiles in 34-form
            GREENS            all tiles that are pure green in color in 34-form
            RED_BONUS         all red bonus tiles in 136-form
            <-- TYPE: integer  ----------------------------------------------->
            EAST, SOUTH, WEST, NORTH     wind tile in 34-form
            BLANK, FORTUNE, CENTER       dragon tile in 34-form
            RED_MAN, RED_PIN, RED_SOU    red bonus tile in 136-form
        --------------------------------------------------------------------------------------------------------------
    """

    his_to_34_dic = {11: 0, 12: 1, 13: 2, 14: 3, 15: 4, 16: 5, 17: 6, 18: 7, 19: 8,
                 21: 9, 22: 10, 23: 11, 24: 12, 25: 13, 26: 14, 27: 15, 28: 16, 29: 17,
                 31: 18, 32: 19, 33: 20, 34: 21, 35: 22, 36: 23, 37: 24, 38: 25, 39: 26,
                 41: 27, 42: 28, 43: 29, 44: 30, 45: 31, 46: 32, 47: 33,
                 51: 4, 52: 13, 53: 22}

    his34_to_34_dic = {34: 4, 35: 13, 36: 22}

    bns_ind_bd_dic = {8: 0, 17: 9, 26: 18, 30: 27, 33: 31, 34: 5, 35: 14, 36: 23}

    to_graph_list = [
        "🀇", "🀈", "🀉", "🀊", "🀋", "🀌", "🀍", "🀎", "🀏", "🀙", "🀚", "🀛", "🀜", "🀝", "🀞", "🀟", "🀠", "🀡",
        "🀐", "🀑", "🀒", "🀓", "🀔", "🀕", "🀖", "🀗", "🀘", "🀀", "🀁", "🀂", "🀃", "🀆", "🀅", "🀄", "[🀋]", "[🀝]",
        "[🀔]"
    ]

    EAST, SOUTH, WEST, NORTH, BLANK, FORTUNE, CENTER = 27, 28, 29, 30, 31, 32, 33
    WINDS, THREES, HONORS = [27, 28, 29, 30], [31, 32, 33], [27, 28, 29, 30, 31, 32, 33]
    ONES, NINES, TERMINALS = [0, 9, 18], [8, 17, 26], [0, 8, 9, 17, 18, 26]
    ONENINE = [0, 8, 9, 17, 18, 26, 27, 28, 29, 30, 31, 32, 33]
    GREENS = [19, 20, 21, 23, 25, 32]
    RED_MAN, RED_PIN, RED_SOU = 16, 52, 88
    RED_BONUS = [16, 52, 88]

    index_to_chow = [[0, 1, 2], [1, 2, 3], [2, 3, 4], [3, 4, 5], [4, 5, 6], [5, 6, 7], [6, 7, 8],
                     [9, 10, 11], [10, 11, 12], [11, 12, 13], [12, 13, 14], [13, 14, 15], [14, 15, 16], [15, 16, 17],
                     [18, 19, 20], [19, 20, 21], [20, 21, 22], [21, 22, 23], [22, 23, 24], [23, 24, 25], [24, 25, 26]]

    tile_desc_list = ['1m', '2m', '3m', '4m', '5m', '6m', '7m', '8m', '9m',
            '1p', '2p', '3p', '4p', '5p', '6p', '7p', '8p', '9p',
            '1s', '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s',
            'E', 'S', 'W', 'N', 'B', 'F', 'C']

    @staticmethod
    def cal_bonus_tiles(bonus_indicators_34):
        """
        Convert bonus indicators in 34-form to the corresponding bonus tiles in 34-form.
        :param bonus_indicators_34: a single integer or a list of integer
        :return: a list of the corresponding bonus tiles
        """
        if isinstance(bonus_indicators_34, int):
            return [Tile.bns_ind_bd_dic.get(bonus_indicators_34, bonus_indicators_34 + 1)]
        if isinstance(bonus_indicators_34, list):
            res = []
            for b in bonus_indicators_34:
                res.append(Tile.bns_ind_bd_dic.get(b, b + 1))
            return res

    @staticmethod
    def t34_to_str(tiles):
        """
        Convert a list of tiles in 34-form to string description
        :param tiles: a list of tiles in 34-form
        :return: a represenation of the tiles in string
        """
        tiles.sort()
        man = [t for t in tiles if t < 9]
        pin = [t - 9 for t in tiles if 9 <= t < 18]
        suo = [t - 18 for t in tiles if 18 <= t < 27]
        chr = [t for t in tiles if t >= 27]
        m = man and (''.join([str(m + 1) for m in man]) + 'm') or ''
        p = pin and ''.join([str(p + 1) for p in pin]) + 'p' or ''
        s = suo and ''.join([str(b + 1) for b in suo]) + 's' or ''
        z = chr and ''.join([Tile.tile_desc_list[ch] for ch in chr]) or ''
        return m + p + s + z

    @staticmethod
    def t136_to_str(tiles):
        """
        Convert a list of tiles in 136-form to string description
        :param tiles: a list of tiles in 136-form
        :return: a represenation of the tiles in string
        """
        tiles34 = [t // 4 for t in tiles]
        return Tile.t34_to_str(tiles34)

    @staticmethod
    def t34_to_grf(tiles):
        """
        Convert tiles in 34-form to unicode graph representation
        :param tiles: a list of tiles or a single tile in 34-form
        :return: a string of the tiles' unicode graph
        """
        if isinstance(tiles, int):
            if tiles >= 0:
                return Tile.to_graph_list[tiles]
        if isinstance(tiles, list):
            if len(tiles) > 0 and isinstance(tiles[0], list):
                graphs = ""
                for meld in tiles:
                    graphs += ''.join([Tile.to_graph_list[t] for t in meld if t >= 0]) + " "
                return graphs
            else:
                graphs = [Tile.to_graph_list[t] for t in tiles if t >= 0]
                return ''.join(graphs)

    @staticmethod
    def t136_to_grf(tiles):
        """
        Convert tiles in 136-form to unicode graph representation
        :param tiles: a list of tiles or a single tile in 136-form
        :return: a string of the tiles' unicode graph
        """
        tiles34 = None
        if isinstance(tiles, int):
            tiles34 = tiles // 4
        if isinstance(tiles, list):
            if len(tiles) > 0 and isinstance(tiles[0], list):
                tiles34 = [[t // 4 for t in m] for m in tiles]
            else:
                tiles34 = [t // 4 for t in tiles]
        if tiles34:
            return Tile.t34_to_grf(tiles34)
        else:
            return ""

    @staticmethod
    def his_to_34(tiles):
        """
        Convert tiles in game log data form to 34-form. In game logs, tiles are represented as follows:
            11-19 <=> 1-9 man
            21-29 <=> 1-9 pin
            31-39 <=> 1-9 suo
            41-47 <=> E, S, W, N, B, F, C
            51, 52, 53 <=> red 5 man, red 5 pin, red 5 suo
        :param tiles: a single tile or a list of tiles in game log data form
        :return: a list of tiles in 34-form
        """
        if isinstance(tiles, int):
            return Tile.his_to_34_dic[tiles]
        elif isinstance(tiles, list):
            return [Tile.his_to_34_dic[t] for t in tiles]
        else:
            raise TypeError

    @staticmethod
    def t60_to_bns(tiles60):
        """
        Convert bonus indicators in game log form to the corresponding bonus tiles in 34-form
        :param tiles60: a single tile or a list of tiles in game log form
        :return: a single or a list of bonus tiles in 34-form
        """
        if isinstance(tiles60, int):
            return Tile.bns_ind_bd_dic.get(Tile.his_to_34(tiles60), Tile.his_to_34(tiles60) + 1)
        elif isinstance(tiles60, list):
            return [Tile.bns_ind_bd_dic.get(t, t + 1) for t in Tile.his_to_34(tiles60)]
        else:
            print("Wrong parameters: Tile.indicator_to_bonus(tiles60)")

    @staticmethod
    def self_wind(dealer):
        """
        Calculate self bonus wind given the seat number of the dealer. The bot always has seat number 0, the player
        right next to the bot has seat number 1, and vice versa...
        :param dealer: the seat number of dealer
        :return: bot's self bonus wind in 34-form
        """
        return Tile.WINDS[(4 - dealer):] + Tile.WINDS[0:(4 - dealer)]

    @staticmethod
    def same_type(tile34_1, tile34_2):
        """
        Check whether the two observed tiles are of the same tile type.
        :param tile34_1: the first tile in 34-form
        :param tile34_2: the second tile in 34-form
        :return: a boolean which indicates whether they are of the same type
        """
        return tile34_1 // 9 == tile34_2 // 9


class Meld:
    """
        Intention of using this class:
            A meld is a set of tiles which satisfy a certain constraint. Mahjong is a contraints satisfactory
            optimisation problem. Basically one can represent a meld just by a list of integers, where each integer
            stands for a certain kind of tile. This class pack other information along with the tiles together to
            satisfy the needs of the client of tenhou.net
    """

    CHI = 'chi'
    PON = 'pon'
    KAN = 'kan'
    CHANKAN = 'chankan'
    NUKI = 'nuki'

    def __init__(self, type=None, tiles=None, open=True, called=None, from_whom=None, by_whom=None):
        """
        To initialise a class instance of meld.
        :param type: the type of the meld, can be chi, pon, kan, chankan
        :param tiles: all the meld tiles in 136 form, e.g. a pon: 4(2m),5(2m),7(2m)
        :param open: all pons and chows are open, but kan can be closed, a closed kan is when one makes a kan all by
        self drawn tiles
        :param called: the tile in 136-form, which was a opponent's discard and one has made the meld with this tile
        :param from_whom: indicates which opponent's discard was taken
        :param by_whom: indicates who has called the meld
        """
        self.type = type
        self.tiles = tiles
        self.open = open
        self.called_tile = called
        self.from_whom = from_whom
        self.by_whom = by_whom

    def __str__(self):
        """
        Represent the meld in unicode graph form
        :return: a string of unicode graph form of the meld
        """
        return '{}, {}'.format(
            self.type, Tile.t136_to_grf(self.tiles), self.tiles
        )

    def __repr__(self):
        return self.__str__()

    @property
    def tiles_34(self):
        """
        Getter: Convert the meld tiles to 34-form
        :return: a list of meld tiles in 34-form
        """
        return [x//4 for x in self.tiles]

    @property
    def tiles_graph(self):
        """
        Getter: Convert the meld tiles to unicode graph form
        :return: a string of unicode graph representation of the meld tiles
        """
        return Tile.t136_to_grf(self.tiles)

    @property
    def tiles_string(self):
        """
        Getter: Convert the meld tiles to string form
        :return: a string which represents the meld tiles
        """
        return Tile.t136_to_str(self.tiles)


class Partition:

    @staticmethod
    def _partition_single_type(tiles34):
        """
        Partition tiles of one type into melds, half-finished melds and singles
        :param tiles34: tiles of the same type
        :return: a list of multiple partition results, each partition result is a list of list, where each list in a
        partition represents a partitioned component
        """
        len_t = len(tiles34)

        # no tiles of this type
        if len_t == 0:
            return [[]]
        # one tile, or two tile which can be parsed into an open set
        if len_t == 1 or (len_t == 2 and abs(tiles34[0] - tiles34[1]) < 3):
            return [[tiles34]]
        # two separate tiles
        if len_t == 2:
            return [[tiles34[0:1], tiles34[1:2]]]

        res = []

        # parse a pon meld
        if tiles34[0] == tiles34[1] == tiles34[2]:
            tmp_res = Partition._partition_single_type(tiles34[3:])
            if len(tmp_res) > 0:
                for tile_set in tmp_res:
                    res.append([tiles34[0:3]] + tile_set)

        # parse a chow meld
        if tiles34[0] + 1 in tiles34 and tiles34[0] + 2 in tiles34:
            rec_tiles = deepcopy(tiles34)
            rec_tiles.remove(tiles34[0])
            rec_tiles.remove(tiles34[0] + 1)
            rec_tiles.remove(tiles34[0] + 2)
            tmp_res = Partition._partition_single_type(rec_tiles)
            if len(tmp_res) > 0:
                for tile_set in tmp_res:
                    res.append([[tiles34[0], tiles34[0] + 1, tiles34[0] + 2]] + tile_set)

        # parse an two-headed half-finished meld
        if tiles34[0] + 1 in tiles34:
            rec_tiles = deepcopy(tiles34)
            rec_tiles.remove(tiles34[0])
            rec_tiles.remove(tiles34[0] + 1)
            tmp_res = Partition._partition_single_type(rec_tiles)
            if len(tmp_res) > 0:
                for tile_set in tmp_res:
                    res.append([[tiles34[0], tiles34[0] + 1]] + tile_set)

        # parse an dead half-finished meld
        if tiles34[0] + 2 in tiles34:
            rec_tiles = deepcopy(tiles34)
            rec_tiles.remove(tiles34[0])
            rec_tiles.remove(tiles34[0] + 2)
            tmp_res = Partition._partition_single_type(rec_tiles)
            if len(tmp_res) > 0:
                for tile_set in tmp_res:
                    res.append([[tiles34[0], tiles34[0] + 2]] + tile_set)

        # parse a pair
        if tiles34[0] == tiles34[1]:
            tmp_res = Partition._partition_single_type(tiles34[2:])
            if len(tmp_res) > 0:
                for tile_set in tmp_res:
                    res.append([tiles34[0:2]] + tile_set)

        tmp_res = Partition._partition_single_type(tiles34[1:])
        if len(tmp_res) > 0:
            for tile_set in tmp_res:
                res.append([tiles34[0:1]] + tile_set)

        tuned_res = []
        min_len = min([len(p) for p in res])
        for p in res:
            if len(p) <= min_len and p not in tuned_res:
                tuned_res.append(p)

        return tuned_res

    @staticmethod
    def partition(tiles34):
        """
        Partition a set of tiles in 34-form into finished melds, half-finished melds and singles.
        :param tiles34:
            a list of tiles in 34-form
        :return:
            a list of partition results of the input tiles, each partition is a list of list,
            where each list represents a partitioned component
        """
        p_man = Partition._partition_single_type([t for t in tiles34 if 0 <= t < 9])
        p_pin = Partition._partition_single_type([t for t in tiles34 if 9 <= t < 18])
        p_suo = Partition._partition_single_type([t for t in tiles34 if 18 <= t < 27])
        h_chr = [t for t in tiles34 if 27 <= t < 34]
        p_chr = [[[chr_tile] * h_chr.count(chr_tile) for chr_tile in set(h_chr)]]
        res = []
        for pm in p_man:
            for pp in p_pin:
                for ps in p_suo:
                    for pc in p_chr:
                        res.append(pm + pp + ps + pc)
        return res

    @staticmethod
    def partition_winning_tiles(hand34, final_tile):
        hand_total = hand34 + [final_tile]
        hand_total_set = set(hand_total)
        res = []

    @staticmethod
    def _shantin_normal(partitions, called_meld_num):

        def geo_vec_normal(p):
            geo_vec = [0] * 6

            def incre(set_type):
                geo_vec[set_type] += 1

            for m in p:
                len(m) == 1 and incre(0)
                len(m) == 2 and abs(m[0] - m[1]) == 0 and incre(3)
                len(m) == 2 and abs(m[0] - m[1]) == 1 and incre(2 if m[0] % 9 > 0 and m[1] % 9 < 8 else 1)
                len(m) == 2 and abs(m[0] - m[1]) == 2 and incre(1)
                len(m) == 3 and incre(5 if m[0] == m[1] else 4)

            return geo_vec

        def shantin_n(p):
            geo_vec = geo_vec_normal(p)
            needed_set = (4 - called_meld_num) - geo_vec[4] - geo_vec[5]
            if geo_vec[3] > 0:
                if geo_vec[1] + geo_vec[2] + geo_vec[3] - 1 >= needed_set:
                    return needed_set - 1
                else:
                    return 2 * needed_set - (geo_vec[1] + geo_vec[2] + geo_vec[3] - 1) - 1
            else:
                if geo_vec[1] + geo_vec[2] >= needed_set:
                    return needed_set
                else:
                    return 2 * needed_set - (geo_vec[1] + geo_vec[2])

        return min([shantin_n(p) for p in partitions])

    @staticmethod
    def shantin_normal(tiles34, called_melds):
        """
        Calculate the normal shantin of a list of tiles.
        Normal shantin means that there is no any extra constraint on the winning tiles' pattern.
        :param tiles34:
            a list of tiles in 34-form, normally it is meant to be the tiles in hand
        :param called_melds:
            the ever called melds
        :return:
            the normal shantin.
        """
        return Partition._shantin_normal(Partition.partition(tiles34), len(called_melds))

    @staticmethod
    def _shantin_pinhu(partitions, called_meld_num, bonus_chrs):
        if called_meld_num:
            return 10

        def geo_vec_pinhu(p):
            geo_vec = [0] * 6

            def incre(set_type):
                geo_vec[set_type] += 1

            for m in p:
                len(m) == 1 and incre(0)
                len(m) == 2 and abs(m[0] - m[1]) == 0 and m[0] not in bonus_chrs and incre(3)
                len(m) == 2 and abs(m[0] - m[1]) == 1 and incre(2 if m[0] % 9 > 0 and m[1] % 9 < 8 else 1)
                len(m) == 2 and abs(m[0] - m[1]) == 2 and incre(1)
                len(m) == 3 and incre(5 if m[0] == m[1] else 4)

            return geo_vec

        def shantin_ph(p):
            geo = geo_vec_pinhu(p)
            need_chow = 4 - geo[4]
            if geo[1] + geo[2] >= need_chow:
                return (geo[3] == 0) + need_chow - 1 + (geo[2] == 0)
            else:
                return (geo[3] == 0) + need_chow - 1 + need_chow - geo[1] - geo[2]

        return min(shantin_ph(p) for p in partitions)

    @staticmethod
    def shantin_no_triplets(tiles34, called_melds, bonus_chrs):
        """
        Calculate the shantin of reaching a "no triplets" waiting hand.
        (1) A "No triplets" hand means the expected winning hand tiles has no pons(triplets)
        (2) There can be only chows(sequences),
        (3) The pair should not be any kind of bonus character tiles!
        :param tiles34:
            A list of tiles in 34-form, usually the tiles in hand
        :param called_melds:
            The ever called melds.
            When any kind of meld if called, the form "pinhu" is not any more constructable
        :param bonus_chrs:
            A list of character tiles that are the bot's yaki tiles
        :return:
            The shantin of "No triplets" form
        """
        partitions = Partition.partition(tiles34)
        return Partition._shantin_pinhu(partitions, len(called_melds), bonus_chrs)

    @staticmethod
    def _shantin_no19(partitions, called_melds):
        for m in called_melds:
            if any(tile in Tile.ONENINE for tile in m):
                return 10

        def geo_vec_no19(p):
            geo_vec = [0] * 6

            def incre(set_type):
                geo_vec[set_type] += 1

            for m in p:
                if m[0] > 26:
                    continue
                len(m) == 1 and 0 < m[0] % 9 < 8 and incre(0)
                len(m) == 2 and abs(m[0] - m[1]) == 0 and 0 < m[0] % 9 < 8 and incre(3)
                len(m) == 2 and abs(m[0] - m[1]) == 1 and m[0] % 9 > 1 and m[1] % 9 < 7 and incre(2)
                len(m) == 2 and abs(m[0] - m[1]) == 1 and (m[0] % 9 == 1 or m[1] % 9 == 7) and incre(1)
                len(m) == 2 and abs(m[0] - m[1]) == 2 and m[0] % 9 > 0 and m[1] % 9 < 8 and incre(1)
                len(m) == 3 and m[0] == m[1] and 0 < m[0] % 9 < 8 and incre(5)
                len(m) == 3 and m[0] != m[1] and incre(4 if m[0] % 9 > 0 and m[2] % 9 < 8 else 1)

            return geo_vec

        def shantin_no19(p):
            geo_vec = geo_vec_no19(p)
            needed_set = (4 - len(called_melds)) - geo_vec[4] - geo_vec[5]
            if geo_vec[3] > 0:
                if geo_vec[1] + geo_vec[2] + geo_vec[3] - 1 >= needed_set:
                    return needed_set - 1
                else:
                    need_single = needed_set - (geo_vec[1] + geo_vec[2] + geo_vec[3] - 1)
                    if geo_vec[0] >= need_single:
                        return 2 * needed_set - (geo_vec[1] + geo_vec[2] + geo_vec[3] - 1) - 1
                    else:
                        return 2 * needed_set - (geo_vec[1] + geo_vec[2] + geo_vec[3] - 1) - 1 + need_single - geo_vec[
                            0]
            else:
                if geo_vec[1] + geo_vec[2] >= needed_set:
                    return needed_set + (geo_vec[0] == 0)
                else:
                    need_single = needed_set - (geo_vec[1] + geo_vec[2]) + 1
                    if geo_vec[0] >= need_single:
                        return 2 * needed_set - (geo_vec[1] + geo_vec[2])
                    else:
                        return 2 * needed_set - (geo_vec[1] + geo_vec[2]) + need_single - geo_vec[0]

        return min(shantin_no19(p) for p in partitions)

    @staticmethod
    def shantin_no_19(tiles34, called_melds):
        """
        Calculate the shantin of "no19" form.
        A "no19" hand mean the expected winning hand tiles only contain tiles from number 2 to 8.
        :param tiles34:
            A list of tiles in 34-form, usually the tiles in hand
        :param called_melds:
            The ever called melds
        :return:
            The shantin of no19 form
        """
        partitions = Partition.partition(tiles34)
        return Partition._shantin_no19(partitions, called_melds)

    @staticmethod
    def shantin_no_sequences(tiles34, called_melds):
        """
        Calculate the shantin of "No sequence" form.
        A "No sequence" from means that the expected winning tiles has no chow(sequence) melds
        :param tiles34:
            A list of tiles in 34-form, usually the hand tiles
        :param called_melds:
            The ever called melds
        :return:
            The shantin of pph form
        """
        if any(len(m) > 1 and m[0] != m[1] for m in called_melds):
            return 10
        num_kezi = len([tile for tile in set(tiles34) if tiles34.count(tile) == 3])
        num_pair = len([tile for tile in set(tiles34) if tiles34.count(tile) == 2])
        need_kezi = 4 - len(called_melds) - num_kezi
        return (need_kezi - 1) if (num_pair >= need_kezi + 1) else (2 * need_kezi - num_pair)

    @staticmethod
    def shantin_seven_pairs(tiles34, called_melds):
        """
        Calculate shantin of form "Seven pairs".
        A "Seven pairs" form means the expected winning tiles are 7 pairs
        :param tiles34:
            A list of tiles in 34-form, usually the hand tiles
        :param called_melds:
            The ever called melds
        :return:
            The shantin of form "Seven pairs"
        """
        if len(called_melds) > 0:
            return 10
        else:
            num_pair = len([tile for tile in set(tiles34) if tiles34.count(tile) >= 2])
            return 6 - num_pair

    @staticmethod
    def _shantin_pure_color(tiles34, called_melds, partitions):
        qh_type = []

        if len(called_melds) > 0:
            meld_types = []
            for m in called_melds:
                if m[0] // 9 == 3:
                    continue
                if m[0] // 9 not in meld_types:
                    meld_types.append(m[0] // 9)
            if len(meld_types) > 1:
                return 10
            else:
                qh_type = meld_types

        if (len(qh_type) == 0 and len(called_melds) > 0) or len(called_melds) == 0:
            type_geo = [
                len([t for t in tiles34 if 0 <= t < 9]),
                len([t for t in tiles34 if 9 <= t < 18]),
                len([t for t in tiles34 if 18 <= t < 27])
            ]
            max_num = max(type_geo)
            qh_type = [i for i in range(3) if type_geo[i] == max_num]

        if len(qh_type) == 0:
            return 10

        def geo_vec_qh(p, tp):
            allowed_types = [tp, 3]
            geo_vec = [0] * 6

            def incre(set_type):
                geo_vec[set_type] += 1

            for m in p:
                if m[0] // 9 in allowed_types:
                    len(m) == 1 and incre(0)
                    len(m) == 2 and abs(m[0] - m[1]) == 0 and incre(3)
                    len(m) == 2 and abs(m[0] - m[1]) == 1 and incre(2 if m[0] % 9 > 0 and m[1] % 9 < 8 else 1)
                    len(m) == 2 and abs(m[0] - m[1]) == 2 and incre(1)
                    len(m) == 3 and incre(5 if m[0] == m[1] else 4)
            return geo_vec

        def shantin_n(p, tp):
            geo_vec = geo_vec_qh(p, tp)
            # print(geo_vec)
            s, p, o, f = geo_vec[0], geo_vec[3], geo_vec[1] + geo_vec[2], geo_vec[4] + geo_vec[5]
            if p > 0:
                p -= 1
                st = 0
                needed_set = 3 - len(called_melds) - f
                while needed_set > 0:
                    if o > 0:
                        needed_set, o, st = needed_set - 1, o - 1, st + 1
                    elif p > 0:
                        needed_set, p, st = needed_set - 1, p - 1, st + 1
                    elif s > 0:
                        needed_set, st, s = needed_set - 1, st + 2, s - 1
                    else:
                        needed_set, st = needed_set - 1, st + 3
                return st if (o + p) > 0 else (st + 1 if s > 0 else st + 2)
            else:
                st = 0
                needed_set = 4 - len(called_melds) - f
                while needed_set > 0:
                    if o > 0:
                        needed_set, o, st = needed_set - 1, o - 1, st + 1
                    elif s > 0:
                        needed_set, st, s = needed_set - 1, st + 2, s - 1
                    else:
                        needed_set, st = needed_set - 1, st + 3
                return st if s > 0 else st + 1

        def shantin_qh(p):
            return min([shantin_n(p, t) for t in qh_type])

        return min([shantin_qh(p) for p in partitions])

    @staticmethod
    def shantin_pure_color(tiles34, called_melds):
        """
        Calculate the shantin of "pure color" form.
        A "pure color" form means the expected winning tiles contain only character tiles and one other type of tiles.
        :param tiles34:
            A list of tiles in 34-form
        :param called_melds:
            The ever called melds
        :return:
            The shantin of "pure color"
        """
        partitions = Partition.partition(tiles34)
        return Partition._shantin_pure_color(tiles34, called_melds, partitions)

    @staticmethod
    def shantin_multiple_forms(tiles34, called_melds, bonus_chrs):
        """
        Calculate shantin of different forms.
        It's an assemble of the various single shantin calculation function
        :param tiles34:
            A list of tiles in 34-form
        :param called_melds:
            The ever called melds
        :param bonus_chrs:
            A list of bonus character tiles
        :return:
            A dictionary, which has the special form name as key and the corresponding shantin as value
        """
        res = {}
        partitions = Partition.partition(tiles34)
        res["normal______"] = Partition._shantin_normal(partitions, len(called_melds))
        res["no_triplets_"] = Partition._shantin_pinhu(partitions, len(called_melds), bonus_chrs)
        res["no_19_______"] = Partition._shantin_no19(partitions, called_melds)
        res["no_sequences"] = Partition.shantin_no_sequences(tiles34, called_melds)
        res["seven_pairs_"] = Partition.shantin_seven_pairs(tiles34, called_melds)
        res["pure_color__"] = Partition._shantin_pure_color(tiles34, called_melds, partitions)
        return res


class WinWaitCal:

    @staticmethod
    def score_calculation_base(han, fu, is_dealer, is_zimo):
        """
        Calculate the base score knowing the han and fu value.
        Fu is a value which stands for a base point, and han is the exponential factor of final scores.
        The very basic score calculation is as follows, while it involves more other details.
            ---------------------------------------------------
            |       base_score = fu * (2 ** (han + 2))        |
            ---------------------------------------------------
        :param han:
            A han is the unit of yaku, yaku is a special pattern that the winning tiles have satisfied.
            Multiples yakus can be achieved at the same time, and thus han is the sum of all yaku values.
            Please check in this namespace the the function han_calculation(...)
        :param fu:
            Fu is the unit for base points, the calculation of fu is beyong complicated
            For calculation of Fu please check the function fu_calculation(...) in this namespace
        :param is_dealer:
            whether the observed player is a dealer
        :param is_zimo:
            whether the observed player has won by self drawn tile or not
        :return:
            a tuple (integer score, string description)
        """
        if han == 0:
            return 0, ''
        elif han < 5:  # when han < 5, the fu has influence on the final point
            if (fu >= 40 and han >= 4) or (fu >= 70 and han >= 3):
                if is_dealer:
                    return 12000, "満貫4000点∀" if is_zimo else "満貫12000点"
                else:
                    return 8000, "満貫2000-4000点" if is_zimo else "満貫8000点"
            base_score = fu * (2 ** (han + 2))
            if is_zimo:
                if is_dealer:
                    each = ((base_score * 2 - 1) // 100 + 1) * 100
                    return each * 3, "{}符{}Han{}点∀".format(fu, han, each)
                else:
                    dscore = ((base_score * 2 - 1) // 100 + 1) * 100
                    xscore = ((base_score - 1) // 100 + 1) * 100
                    return dscore + 2 * xscore, "{}符{}Han{}-{}点".format(fu, han, xscore, dscore)
            else:
                score = ((base_score * 6 - 1) // 100 + 1) * 100 if is_dealer else ((base_score * 4 - 1) // 100 + 1) * 100
                return score, "{}符{}Han{}点".format(fu, han, score)
        elif han == 5: # when han >= 5, the fu does not make any difference to final score
            if is_dealer:
                return 12000, "満貫4000点∀" if is_zimo else "満貫12000点"
            else:
                return 8000, "満貫2000-4000点" if is_zimo else "満貫8000点"
        elif 6 <= han <= 7:
            if is_dealer:
                return 18000, "跳满6000点∀" if is_zimo else "跳满18000点"
            else:
                return 12000, "跳满3000-6000点" if is_zimo else "跳满12000点"
        elif 8 <= han <= 10:
            if is_dealer:
                return 24000, "倍满8000点∀" if is_zimo else "倍满24000点"
            else:
                return 16000, "倍满4000-8000点" if is_zimo else "倍满16000点"
        elif 11 <= han <= 12:
            if is_dealer:
                return 36000, "三倍满12000点∀" if is_zimo else "三倍满36000点"
            else:
                return 24000, "三倍满6000-12000点" if is_zimo else "三倍满24000点"
        else:
            if is_dealer:
                return 48000, "役满16000点∀" if is_zimo else "役满48000点"
            else:
                return 32000, "役满8000-16000点" if is_zimo else "役满32000点"

    @staticmethod
    def fu_calculation(hand_partition, final_tile, melds, minkan, ankan, is_zimo, player_wind, round_wind):
        """
        Calculate the Fu of the winning tiles.
        Fu is sort of multiplier for the base socre, since base_score = fu * (2 ** (han + 2))
        :param hand_partition:
            List of list, it's a partition of hand tiles
        :param final_tile:
            Integer, the final tile with which the observed player has won
        :param melds:
            List of list, triplets and sequences melds of the observed player
        :param minkan:
            List of list, minkan melds of the observed player
        :param ankan:
            List of list, ankan melds of the observed player
        :param is_zimo:
            Boolean, Whether the observed player has won by self drawn tile or not
        :param player_wind:
            Integer, indicates what is the wind tile which adds yaku for the observed player
        :param round_wind:
            Integer, indicates what is the wind tiles which ass yaku for all players at table
        :return:
            A dict, {description of the value : value}
                res["fu"] = a dict, key=fu type, value=fu value
                res["fu_sum"] = integer, raw sum of fu values
                res["fu_round"] = integer, rounded sum of fu values
                res["fu_desc"] = string, showing what fu types are achieved
        """
        if len(hand_partition) == 7:
            return {"fu": {"七对(25Fu)": 25}, "fu_sum": 25, "fu_round": 25, "fu_desc": "七对(25Fu)"}

        if len(hand_partition) + len(melds) == 5:
            chows = [m for m in hand_partition + melds if m[0] != m[1]]
            pair = [m for m in hand_partition if len(m) == 2][0]
            if len(chows) == 4 and pair[0] not in Tile.THREES + [player_wind, round_wind]:
                chows_with_final = [chow for chow in chows if final_tile in chow]
                if any((chw[0] == final_tile and chw[0] % 9 != 6) or (chw[2] == final_tile and chw[2] % 9 != 2)
                           for chw in chows_with_final):
                    if is_zimo and len(melds) == 0:
                        return {"fu": {"門前清自摸和平和(20Fu)": 20}, "fu_sum": 20, "fu_round": 20, "fu_desc": "門前清自摸和平和(20Fu)"}
                    if not is_zimo and len(melds) > 0:
                        return {"fu": {"非门清平和荣和(30Fu)": 30}, "fu_sum": 30, "fu_round": 30, "fu_desc": "非门清平和荣和(30Fu)"}

        fu = {}

        def add_base(b, b_desc):
            fu[b_desc] = b

        def check_kezi():
            for meld in hand_partition:
                if len(meld) == 3:
                    if meld[0] == meld[1] == meld[2]:
                        if meld[0] in Tile.ONENINE:
                            if is_zimo or final_tile != meld[0]:
                                add_base(8, "幺九暗刻(8Fu)")
                            else:
                                add_base(4, "幺九明刻(4Fu)")
                        else:
                            if is_zimo or final_tile != meld[0]:
                                add_base(4, "中张暗刻(4Fu)")
                            else:
                                add_base(2, "中张明刻(2Fu)")

            for meld in melds:
                if meld[0] == meld[1]:
                    if meld[0] in Tile.ONENINE:
                        add_base(4, "幺九明刻(4Fu)")
                    else:
                        add_base(2, "中张明刻(2Fu)")

        def check_kans():
            for mk in minkan:
                if mk[0] in Tile.ONENINE:
                    add_base(16, "幺九明杠(16Fu)")
                else:
                    add_base(8, "中张明杠(8Fu)")
            for ak in ankan:
                if ak[0] in Tile.ONENINE:
                    add_base(32, "幺九暗杠(32Fu)")
                else:
                    add_base(16, "中张暗杠(16Fu)")

        def check_pair(p):
            if p[0] in Tile.THREES:
                add_base(2, "役牌雀头(2Fu)")
            if p[0] == player_wind:
                add_base(2, "自风雀头(2Fu)")
            if p[0] == round_wind:
                add_base(2, "场风雀头(2Fu)")

        def check_waiting_type(p):
            chws = [m for m in hand_partition + melds if m[0] != m[1]]
            chws_with_final = [chow for chow in chws if final_tile in chow]
            if p[0] == final_tile and len(chws_with_final) == 0:
                add_base(2, "单吊(2Fu)")
            elif len(chws_with_final) > 0:
                if all((chw[1] == final_tile or (chw[0] == final_tile and chw[2] % 9 == 8)
                        or (chw[2] == final_tile and chw[0] % 9 == 0)) for chw in chws_with_final):
                    add_base(2, "边张嵌张胡牌(2Fu)")

        def check_win_type():
            if is_zimo:
                add_base(2, "自摸(2Fu)")
            if not is_zimo and len(melds + minkan) == 0:
                add_base(10, "门前清荣胡(10Fu)")

        pair = [m for m in hand_partition if len(m) == 2][0]
        check_kezi()
        check_kans()
        check_pair(pair)
        check_waiting_type(pair)
        check_win_type()

        res = dict()
        res["fu"] = fu
        res["fu_sum"] = sum([v for k, v in fu.items()])
        res["fu_round"] = ((res["fu_sum"] - 1) // 10 + 1) * 10
        res["fu_desc"] = " ".join([k for k, v in fu.items()])
        return res

    @staticmethod
    def han_calculation(hand_partition, final_tile, melds, minkan, ankan, is_zimo, player_wind, round_wind, reach):
        """
        Calculate the han value.
        Han is a unit of yaku.
        Yakuman is another unit of yaku, which means maxi!
        A Yaku is a special pattern that the winning tiles satisfy.
        Each extra han would potentially double the final point up to a limit, since
            ---------------------------------------------------
            |       base_score = fu * (2 ** (han + 2))        |
            ---------------------------------------------------
        See score_calculation() in this class

        :param hand_partition:
            List of list, it's a partition of hand tiles
        :param final_tile:
            Integer, the final tile with which the observed player has won
        :param melds:
            List of list, triplets and sequences melds of the observed player
        :param minkan:
            List of list, minkan melds of the observed player
        :param ankan:
            List of list, ankan melds of the observed player
        :param is_zimo:
            Boolean, Whether the observed player has won by self drawn tile or not
        :param player_wind:
            Integer, indicates what is the wind tile which adds yaku for the observed player
        :param round_wind:
            Integer, indicates what is the wind tiles which ass yaku for all players at table
        :param reach:
            Boolean, whether the observed player has called Riichi
        :return:
            A dict, {description of the value : value}
                res["han"] = a dict, key=the yaku, value=the corresponding han value
                res["ykman"] = a dict, key=the yakuman, value=the corresponding yakuman value
                res["han_sum"] = integer, sum of all han values
                res["yk_sum"] = integer, sum of yakumans
                res["han_desc"] = string, all yakus that are achieved

        """
        han, ykman = {}, {}

        def add_han(h, h_desc):
            han[h_desc] = h

        def add_yakuman(m, m_desc):
            ykman[m_desc] = m

        all_melds = hand_partition + melds + minkan + ankan
        all_melds_no_kan = hand_partition + melds
        all_tiles = [tile for meld in all_melds for tile in meld]
        is_menqing = len(melds + minkan) == 0
        len_open = len(melds + minkan + ankan)
        len_total = len_open + len(hand_partition)

        def check_all_single_one_nine():
            if len(hand_partition) == 13:
                add_yakuman(1, "国士無双(Maxi)")

        def check_seven_pairs():
            if len(hand_partition) == 7:
                add_han(2, "七対子(2Han)")

        def check_win_type():
            if reach:
                add_han(1, "立直(1Han)")
            if is_zimo and is_menqing:
                add_han(1, "門前清自摸和(1Han)")

        def check_dori():
            for meld in all_melds:
                if len(meld) > 2 and meld[0] == meld[1]:
                    if meld[0] in Tile.THREES:
                        add_han(1, "役牌(1Han)")
                    if meld[0] == player_wind:
                        add_han(1, "自風(1Han)")
                    if meld[0] == round_wind:
                        add_han(1, "場風(1Han)")

        def check_no19():
            if all(t not in all_tiles for t in Tile.ONENINE):
                add_han(1, "断幺九(1Han)")

        def check_3chows_same_color():
            if len_total == 5:
                chows = list()
                for meld in all_melds_no_kan:
                    if len(meld) == 3 and meld[0] != meld[1]:
                        chows.append(meld)
                if len(chows) > 2:
                    for i in range(0, 7):
                        if all([i + t + 0, i + t + 1, i + t + 2] in chows for t in [0, 9, 18]):
                            if is_menqing:
                                add_han(2, "三色同順(2Han)")
                            else:
                                add_han(1, "三色同順(1Han)")
                            break

        def check_flat_win():
            if is_menqing and len(hand_partition) == 5:
                chows = [meld for meld in hand_partition if len(meld) == 3 and meld[0] != meld[1]]
                try:
                    pair = [meld for meld in hand_partition if len(meld) == 2][0]
                except:
                    print(hand_partition)
                    pair = [meld for meld in hand_partition if len(meld) == 2][0]
                if len(chows) == 4 and pair[0] not in Tile.THREES + [player_wind, round_wind]:
                    chows_with_final = [chow for chow in chows if final_tile in chow]
                    if any((chw[0] == final_tile and chw[0] % 9 != 6) or (chw[2] == final_tile and chw[2] % 9 != 2)
                           for chw in chows_with_final):
                        add_han(1, "平和(1Han)")

        def check_1to9():
            if len_total == 5:
                for i in [0, 9, 18]:
                    if all([s + i, s + i + 1, s + i + 2] in all_melds_no_kan for s in [0, 3, 6]):
                        if is_menqing:
                            add_han(2, "一気通貫(2Han)")
                        else:
                            add_han(1, "一気通貫(1Han)")
                        break

        def check_all_pons():
            if len_total == 5:
                chows = [meld for meld in all_melds_no_kan if meld[0] != meld[1]]
                if len(chows) == 0:
                    add_han(2, "対々和(2Han)")

        def check_threes():
            if len_total == 5:
                metrics = [all_tiles.count(t) for t in Tile.THREES]
                metrics = [t if t < 4 else 3 for t in metrics]
                if metrics.count(3) == 3:
                    add_yakuman(1, "大三元(Maxi)")
                if metrics.count(3) == 2 and metrics.count(2) == 1:
                    add_han(2, "小三元(2Han)")

        def check_all19():
            # 混老頭(2Han)
            all_19pons = len_total == len([m for m in all_melds if len(m) > 1 and m[0] == m[1] and m[0] in Tile.ONENINE])
            # 純全帯幺九
            pure_all_19 = len_total == 5 == len([m for m in all_melds if any(t in Tile.TERMINALS for t in m)])
            # these four types can not be counted at the same time, only one of them is counted
            if all_19pons and pure_all_19:
                add_yakuman(1, "清老頭(Maxi)")
            elif all_19pons:
                add_han(2, "混老頭(2Han)")
            elif pure_all_19:
                if is_menqing:
                    add_han(3, "純全帯幺九(3Han)")
                else:
                    add_han(2, "純全帯幺九(2Han)")
            else:  # 混全帯幺九
                if len_total == 5 or len_total == 7:
                    if len([m for m in all_melds if any(t in Tile.ONENINE for t in m)]) == len_total:
                        if is_menqing:
                            add_han(2, "混全帯幺九(2Han)")
                        else:
                            add_han(1, "混全帯幺九(1Han)")

        def check_3pons_same_color():
            if len_total == 5:
                for i in range(0, 9):
                    if all([n + i] * 3 in all_melds or [n + i] * 4 in all_melds for n in [0, 9, 18]):
                        add_han(2, "三色同刻(2Han)")
                        break

        def check_3kans():
            if len_total == 5:
                if len(ankan + minkan) == 3:
                    add_han(2, "三槓子(2Han)")

        def check_multiple_same_chow():
            # 二盃口(3Han)
            was_erbeikou = False
            if is_menqing and len(hand_partition) == 5:
                if all(all_tiles.count(t) == 2 for t in set(all_tiles)):
                    was_erbeikou = True
                    add_han(3, "二盃口(3Han)")
            if not was_erbeikou and is_menqing and len(hand_partition + ankan):  # 一盃口
                chows = [m for m in hand_partition if len(m) > 1 and m[0] != m[1]]
                if any(chows.count(chw) >= 2 for chw in chows):
                    add_han(1, "一盃口(1Han)")

        def check_pure_color():
            if any(all(typ <= t < typ + 9 for t in all_tiles) for typ in [0, 9, 18]):
                if is_menqing:
                    add_han(6, "清一色(6Han)")
                else:
                    add_han(5, "清一色(5Han)")
            elif any(all(typ <= t < typ + 9 or 27 <= t < 34 for t in all_tiles) for typ in [0, 9, 18]):
                if is_menqing:
                    add_han(3, "混一色(3Han)")
                else:
                    add_han(2, "混一色(2Han)")

        def check_pure_green():
            if all(t in Tile.GREENS for t in all_tiles):
                add_yakuman(1, "緑一色(Maxi)")

        def check_4ankans():
            if len_total == 5:
                kezi = len(ankan) + len([m for m in hand_partition if len(m) == 3 and m[0] == m[1]])
                pair = [m for m in hand_partition if len(m) == 2][0]
                if kezi == 4:
                    if is_zimo or final_tile == pair[0]:
                        add_yakuman(1, "四暗刻(Maxi)")
                    else:
                        add_han(2, "三暗刻(2Han)")
                else:  # 三暗刻
                    kezi = len(ankan) + len([m for m in hand_partition
                                             if len(m) == 3 and m[0] == m[1] and (is_zimo or final_tile != m[0])])
                    if kezi == 3:
                        add_han(2, "三暗刻(2Han)")

        def check_four_honors():
            metrics = [all_tiles.count(t) for t in Tile.WINDS]
            metrics = [t if t < 4 else 3 for t in metrics]
            if metrics.count(3) == 4:
                add_yakuman(1, "大四喜(Maxi)")
            elif metrics.count(3) == 3 and metrics.count(2) == 1:
                add_yakuman(1, "小四喜(Maxi)")

        def check_all_characters():
            if all(t in Tile.HONORS for t in all_tiles):
                add_yakuman(1, "字一色(Maxi)")

        def check_9lotus():
            if is_menqing:
                for i in [0, 9, 18]:
                    if all(i <= t < i + 9 for t in all_tiles) and all(t in all_tiles for t in range(i, i + 9)):
                        if all_tiles.count(i) > 2 and all_tiles.count(i + 8) > 2:
                            add_yakuman(1, "九蓮宝燈(Maxi)")
                            break

        check_all_single_one_nine()  # 国士無双(Maxi)
        check_seven_pairs()  # 七対子(2Han)
        check_win_type()  # 立直(1Han) 門前清自摸和(1Han)
        check_dori()  # 役牌(1Han) 場風(1Han) 自風(1Han)
        check_no19()  # 断幺九
        check_flat_win()  # 平和(1Han)
        check_1to9()  # 一気通貫(2/1Han)
        check_all_pons()  # 対々和(2Han)
        check_threes()  # 大三元(Maxi) 小三元(2Han)
        check_all19()  # 清老頭(Maxi) 純全帯幺九(3/2Han) 混老頭(2Han) 混全帯幺九(2/1Han)
        check_3pons_same_color()  # 三色同刻
        check_3chows_same_color()  # 三色同順(2/1Han)
        check_3kans()  # 三槓子
        check_multiple_same_chow()  # 二盃口(3Han) 一盃口(1Han)
        check_pure_color()  # 清一色(6/5Han) 混一色(3/2Han)
        check_pure_green()  # 緑一色
        check_4ankans()  # 四暗刻(Maxi)
        check_four_honors()  # 小四喜(Maxi) 大四喜(Maxi)
        check_all_characters()  # 字一色(Maxi)
        check_9lotus()  # 九蓮宝燈(Maxi)

        res = dict()
        res["han"] = han
        res["ykman"] = ykman
        res["han_sum"] = sum([v for k, v in han.items()])
        res["yk_sum"] = sum([v for k, v in ykman.items()])
        res["han_desc"] = " ".join([k for k, v in han.items()]) if res["yk_sum"] == 0 else " ".join([k for k, v in ykman.items()])
        return res

    @staticmethod
    def win_parse(hand34, final_tile):
        """
        To parse current hand tiles into melds which satisfies winning constrains
        :param hand34: tiles remaning in hand
        :param final_tile: the tile with which one finished his hand
        :return: list of list of list, different possibilities of partitioning total titles
        """

        def parse_nums(tiles):
            if len(tiles) == 0:
                return [[[]]]

            if len(tiles) == 1:
                return None

            if len(tiles) == 2:
                return [[tiles]] if tiles[0] == tiles[1] else None

            if len(tiles) == 3:
                ismeld = tiles[0] == tiles[1] == tiles[2] or (tiles[0] + 2) == (tiles[1] + 1) == tiles[2]
                return [[tiles]] if ismeld else None

            if len(tiles) % 3 == 1:
                return None

            res = []

            if len(tiles) % 3 == 2:
                if tiles[0] == tiles[1]:
                    rec_res = parse_nums(tiles[2:])
                    if rec_res:
                        for partition in rec_res:
                            res.append([tiles[0:2]] + partition)

            if tiles[0] == tiles[1] == tiles[2]:
                rec_res = parse_nums(tiles[3:])
                if rec_res:
                    for partition in rec_res:
                        res.append([tiles[0:3]] + partition)

            if (tiles[0] + 1) in tiles and (tiles[0] + 2) in tiles:
                remain_tiles = deepcopy(tiles)
                remain_tiles.remove(tiles[0])
                remain_tiles.remove(tiles[0] + 1)
                remain_tiles.remove(tiles[0] + 2)
                rec_res = parse_nums(remain_tiles)
                if rec_res:
                    for partition in rec_res:
                        res.append([[tiles[0], tiles[0] + 1, tiles[0] + 2]] + partition)

            return res if len(res) > 0 else None

        def parse_chrs(tiles):
            if len(tiles) == 0:
                return [[]]

            if len(tiles) % 3 == 1 or any(tiles.count(t) == 1 for t in tiles):
                return None

            tiles_set = set(tiles)
            partition = [[t] * tiles.count(t) for t in tiles_set]

            return [partition] if len(partition) == (len(tiles) - 1) // 3 + 1 else None

        hand_total = hand34 + [final_tile]
        hand_total_set = set(hand_total)
        res = []
        if all(hand_total.count(t) == 2 for t in hand_total_set) and len(hand_total) == 14:
            res.append([[t] * 2 for t in hand_total_set])

        if all(t in hand_total for t in Tile.ONENINE) and all(t in Tile.ONENINE for t in hand_total):
            return [[[t] * hand_total.count(t) for t in Tile.ONENINE]]

        hand_total.sort()
        hand_man = [t for t in hand_total if t < 9]
        hand_pin = [t for t in hand_total if 9 <= t < 18]
        hand_suo = [t for t in hand_total if 18 <= t < 27]
        hand_chr = [t for t in hand_total if 27 <= t]
        man_parse = parse_nums(hand_man)
        pin_parse = parse_nums(hand_pin)
        suo_parse = parse_nums(hand_suo)
        chr_parse = parse_chrs(hand_chr)
        if hand_man and not man_parse:
            return res
        if hand_pin and not pin_parse:
            return res
        if hand_suo and not suo_parse:
            return res
        if hand_chr and not chr_parse:
            return res

        for a in man_parse:
            for b in pin_parse:
                for c in suo_parse:
                    res.append([m for m in a + b + c + chr_parse[0] if len(m) > 0])
        return res

    @staticmethod
    def score_calculation(hand34, final_tile, melds, minkan, ankan, is_zimo, player_wind, round_wind, reach, bonus_num,
                          bonus_tiles, benchan, reach_stick, is_dealer):
        """
        Calculate the final score given the hand tiles and melds.
        The method score_calculation_base() calculates only the base points.
        In this methods more components are added to deliver the final score.
        There can be different score result depending on how the tiles are partitioned.
        So, the highest possible score will be returned.
        :param hand34:
            List, hand tiles in 34-form
        :param final_tile:
            Integer, the last tile what the observed player has won with, 34-form
        :param melds:
            List of list, the called Triplets/Sequences melds of the observed player
        :param minkan:
            List of list, the called minkan melds of the observed player
        :param ankan:
            List of list, the called ankan melds of the observed player
        :param is_zimo:
            Boolean, whether the observed player has won by self drawn tile
        :param player_wind:
            Integer, the wind tile that adds yaku for the observed player
        :param round_wind:
            Integer, the wind tile that adds yaku for every player at table
        :param reach:
            Boolean, whether the observed player has called Riichi
        :param bonus_num:
            Integer, the number of bonus tiles (dori, red dori)
        :param bonus_tiles:
            List, the bonus tiles
        :param benchan:
            Integer, the number of benchan sticks. This number increases by one when the dealer wins each extra game
            successively.
        :param reach_stick:
            Integer, the number of Riichi sticks. Riichi sticks are passed to next game if the current game didn't
            result in winning and someone has called Riichi.
        :param is_dealer:
            Boolean, whether the observed player is the dealer
        :return:
            A dict, {description of the value : value}
            For example:
                {
                 "score": 13300
                 "score_desc": 20Fu/5Han --> 満貫4000点∀ 13300点
                 "han": {'立直(1Han)': 1, '門前清自摸和(1Han)': 1, '自風(1Han)': 1, '場風(1Han)': 1, '(赤/裏)ドラ(1Han)': 1}
                 "han_desc": 立直(1Han) 門前清自摸和(1Han) 自風(1Han) 場風(1Han) (赤/裏)ドラ(1Han)
                 "fu": {'幺九暗刻(8Fu)': 8, '单吊(2Fu)': 2, '自摸(2Fu)': 2}
                 "fu_desc": 幺九暗刻(8Fu) 单吊(2Fu) 自摸(2Fu)
                 "partition": [[0, 0, 0], [11, 12, 13], [24, 25, 26], [27, 27], [28, 28, 28]]
                 }
        """
        win_partitions = WinWaitCal.win_parse(hand34, final_tile)
        if len(win_partitions) == 0:
            return None
        b_score, b_score_desc, b_han, b_han_desc, b_fu, b_fu_desc, b_par = 0, None, None, None, None, None, None
        bonus_num += final_tile in bonus_tiles
        for p in win_partitions:
            han_dict = WinWaitCal.han_calculation(p, final_tile, melds, minkan, ankan, is_zimo, player_wind, round_wind, reach)
            if han_dict["han_sum"] == han_dict["yk_sum"] == 0:
                continue
            if han_dict["yk_sum"] > 0:
                base_maxi_score = 48000 if is_dealer else 32000
                final_score = base_maxi_score * han_dict["yk_sum"] + 1000 * reach_stick + benchan * 300
                if final_score > b_score:
                    b_score = final_score
                    maxi_desc = han_dict["han_desc"]
                    b_han = han_dict["ykman"]
                    b_score_desc = "役满 {}点 {}点".format(base_maxi_score * han_dict["yk_sum"], final_score)
                    b_han_desc = "{}".format(maxi_desc)
                    b_fu = None
                    b_fu_desc = None
                    b_par = p
            else:
                fu_dict = WinWaitCal.fu_calculation(p, final_tile, melds, minkan, ankan, is_zimo, player_wind, round_wind)
                fu = fu_dict["fu_round"]
                base_point, lose_desc = WinWaitCal.score_calculation_base(han_dict["han_sum"] + bonus_num, fu, is_dealer, is_zimo)
                final_score = base_point + 1000 * reach_stick + benchan * (300 if base_point > 0 else 0)
                score_cal_desc = "{}Fu/{}Han --> {} {}点".format(fu, han_dict["han_sum"] + bonus_num, lose_desc, final_score)
                han_desc = han_dict["han_desc"]
                han_desc += " (赤/裏)ドラ({}Han)".format(bonus_num) if bonus_num > 0 else ""
                if final_score > b_score:
                    b_score = final_score
                    b_score_desc = score_cal_desc
                    b_han = han_dict["han"]
                    if bonus_num > 0:
                        b_han["(赤/裏)ドラ({}Han)".format(bonus_num)] = bonus_num
                    b_han_desc = han_desc
                    b_fu = fu_dict["fu"]
                    b_fu_desc = fu_dict["fu_desc"]
                    b_par = p

        if b_score == 0:
            return None
        else:
            res = dict()
            res["score"] = b_score
            res["score_desc"] = b_score_desc
            res["han"] = b_han
            res["han_desc"] = b_han_desc
            res["fu"] = b_fu
            res["fu_desc"] = b_fu_desc
            res["partition"] = b_par
            return res

    @staticmethod
    def waiting_calculation(hand34, melds, minkan, ankan, is_zimo, player_wind, round_wind, reach, bonus_num,
                            bonus_tiles, benchan, reach_stick, is_dealer):
        """
        Calculate what kinds of tiles is the player waiting, given current hand tiles and melds.
        This function calls score_calculation(...) as subroutines.
        :param hand34:
            List, hand tiles in 34-form
        :param melds:
            List of list, the called Triplets/Sequences melds of the observed player
        :param minkan:
            List of list, the called minkan melds of the observed player
        :param ankan:
            List of list, the called ankan melds of the observed player
        :param is_zimo:
            Boolean, whether the observed player has won by self drawn tile
        :param player_wind:
            Integer, the wind tile that adds yaku for the observed player
        :param round_wind:
            Integer, the wind tile that adds yaku for every player at table
        :param reach:
            Boolean, whether the observed player has called Riichi
        :param bonus_num:
            Integer, the number of bonus tiles (dori, red dori)
        :param bonus_tiles:
            List, the bonus tiles
        :param benchan:
            Integer, the number of benchan sticks. This number increases by one when the dealer wins each extra game
            successively.
        :param reach_stick:
            Integer, the number of Riichi sticks. Riichi sticks are passed to next game if the current game didn't
            result in winning and someone has called Riichi.
        :param is_dealer:
            Boolean, whether the observed player is the dealer
        :return:
            A dict, {waiting tile : dict of the corresponding winning score calculation}
            For example:
                {
                    0:
                        {
                            score     : 49300
                            score_desc: 役满 48000点 49300点
                            han       : {'九蓮宝燈(Maxi)': 1}
                            han_desc  : 九蓮宝燈(Maxi)
                            fu        : None
                            fu_desc   : None
                            partition : [[0, 0, 0], [0, 1, 2], [3, 4, 5], [6, 7, 8], [8, 8]]
                        }

                    1:
                        {
                            score     : 49300
                            score_desc: 役满 48000点 49300点
                            han       : {'九蓮宝燈(Maxi)': 1}
                            han_desc  : 九蓮宝燈(Maxi)
                            fu        : None
                            fu_desc   : None
                            partition : [[0, 0, 0], [1, 1], [2, 3, 4], [5, 6, 7], [8, 8, 8]]
                        }
                    ...
                }
        """
        waitings = {}
        if len(hand34) == 13 and len(set(hand34)) == 7:
            pairs = [t for t in set(hand34) if hand34.count(t) == 2]
            single = [t for t in set(hand34) if hand34.count(t) == 1]
            if len(pairs) == 6 and len(single) == 1:
                waitings[single[0]] = WinWaitCal.score_calculation(hand34, single[0], melds, minkan, ankan, is_zimo,
                                                                   player_wind, round_wind, reach, bonus_num,
                                                                   bonus_tiles, benchan, reach_stick, is_dealer)
        elif len(hand34) == 13 and len(set(hand34)) >= 12:
            metrics_19 = [hand34.count(t) for t in Tile.ONENINE]
            if metrics_19.count(1) == 13:
                for t in Tile.ONENINE:
                    waitings[t] = WinWaitCal.score_calculation(hand34, t, melds, minkan, ankan, is_zimo,
                                                               player_wind, round_wind, reach, bonus_num,
                                                               bonus_tiles, benchan, reach_stick, is_dealer)
            elif metrics_19.count(1) == 11 and metrics_19.count(2) == 1:
                wait = [t for t in Tile.ONENINE if t not in hand34][0]
                waitings[wait] = WinWaitCal.score_calculation(hand34, wait, melds, minkan, ankan, is_zimo,
                                                              player_wind, round_wind, reach, bonus_num,
                                                              bonus_tiles, benchan, reach_stick, is_dealer)
        else:
            lenman = len([t for t in hand34 if t < 9])
            lenpin = len([t for t in hand34 if 9 <= t < 18])
            lensuo = len([t for t in hand34 if 18 <= t < 27])
            lenchr = len([t for t in hand34 if 27 <= t])
            metrics = [l % 3 for l in [lenman, lenpin, lensuo, lenchr]]
            possible_tiles = []
            if 1 in metrics and 2 not in metrics and metrics.count(1) == 1:
                tile_type = metrics.index(1)
                if tile_type < 3:
                    possible_tiles = list(range(tile_type*9, (tile_type+1)*9))
                else:
                    possible_tiles = list(range(27, 34))
            elif 2 in metrics and 1 not in metrics and metrics.count(2) == 2:
                for i in range(3):
                    if metrics[i] == 2:
                        possible_tiles.append(list(range(i*9, (i+1)*9)))
                if metrics[3] == 2:
                    possible_tiles.append(list(range(27, 34)))
            for pt in possible_tiles:
                score_dict = WinWaitCal.score_calculation(hand34, pt, melds, minkan, ankan, is_zimo,
                                                          player_wind, round_wind, reach, bonus_num,
                                                          bonus_tiles, benchan, reach_stick, is_dealer)
                if score_dict:
                    waitings[pt] = score_dict

        return waitings


class GameLogCrawler:

    seed = "Seria"

    level_dict = {'新人': 0, '１級': 1, '２級': 2, '３級': 3, '４級': 4, '５級': 5, '６級': 6, '７級': 7, '８級': 8, '９級': 9,
                  '初段': 10, '二段': 11, '三段': 12, '四段': 13, '五段': 14, '六段': 15, '七段': 16, '八段': 17, '九段': 18,
                  '十段': 19, '天鳳位': 20}

    def __init__(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        dbfile = dir_path + "/gamelog.db"
        self.conn = sqlite3.connect(dbfile)
        self.cs = self.conn.cursor()
        self._db_create_tables_if_not_exists()
        # self.cs.execute(f"CREATE TABLE IF NOT EXISTS ")

    def _db_show_table_structures(self, table_name):
        res = self.cs.execute(f"PRAGMA table_info('{table_name}');").fetchall()
        cnt = self.cs.execute(f"SELECT count(*) from '{table_name}'")
        print("TABLE '{}': {} rows".format(table_name, list(cnt)[0][0]))
        print("      " + "-" * 43 + " ")
        print("    | {:10s} {:10s} {:10s} {:10s}|".format("Column", "Name", "Type", "Primary"))
        print("    | " + "-" * 43 + "|")
        for r in res:
            print("    | {:10s} {:10s} {:10s} {:10s}|".format(str(r[0]), str(r[1]), str(r[2]), str(r[5])))
        print("      " + "-" * 43 + " ")
        print()

    def _db_create_tables_if_not_exists(self):
        self.cs.execute("CREATE TABLE IF NOT EXISTS player ('name' text PRIMARY KEY, 'level' text, 'pt' text, 'lv' INTEGER)")
        self.cs.execute("CREATE TABLE IF NOT EXISTS refids ('ref' text PRIMARY KEY, 'p1' text, 'p2' text, 'p3' text, 'p4' text)")
        self.cs.execute("CREATE TABLE IF NOT EXISTS logs ('refid' text PRIMARY KEY, 'log' text)")
        self.conn.commit()

    def db_prt_players(self, rows=100):
        row_cnt_cs_obj = self.cs.execute("SELECT count(*) FROM player")
        print("There are {} rows in table player!".format(row_cnt_cs_obj.fetchone()[0]))
        for row in self.cs.execute("SELECT * FROM player ORDER BY lv DESC"):
            print("  {}".format(row))
            rows -= 1
            if rows <= 0:
                break

    def db_prt_refs(self, rows=100):
        row_cnt_cs_obj = self.cs.execute("SELECT count(*) FROM refids")
        print("There are {} rows in table refids!".format(row_cnt_cs_obj.fetchone()[0]))
        for row in self.cs.execute("SELECT * FROM refids"):
            print("  {}".format(row))
            rows -= 1
            if rows <= 0:
                break

    def db_prt_logs(self, rows=100):
        row_cnt_cs_obj = self.cs.execute("SELECT count(*) FROM logs")
        print("There are {} rows in table refids!".format(row_cnt_cs_obj.fetchone()[0]))
        for row in self.cs.execute("SELECT * FROM logs"):
            print("  {}".format(row))
            rows -= 1
            if rows <= 0:
                break

    def db_show_tables(self):
        """
        Show the structure of tables in the database
        :return:
        """
        self._db_show_table_structures("player")
        self._db_show_table_structures("refids")
        self._db_show_table_structures("logs")

    def _db_exists_game_log(self, refid):
        has_log = self.cs.execute(f"SELECT count(*) FROM logs WHERE refid = '{refid}'")
        has_log = has_log.fetchone()
        return has_log[0]

    def _db_exists_name(self, name):
        has_name = self.cs.execute(f'SELECT count(*) FROM player WHERE name = "{name}"')
        has_name = has_name.fetchone()
        if not has_name or len(has_name) == 0:
            return False
        return has_name[0] != None and has_name[0] > 0

    def _db_exists_refid(self, refid):
        has_refid = self.cs.execute(f'SELECT count(*) FROM refids WHERE ref = "{refid}"')
        has_refid = has_refid.fetchone()
        if not has_refid or len(has_refid) == 0:
            return False
        return has_refid[0] != None and has_refid[0] > 0

    def _db_insert_names(self, players):
        for name in players:
            try:
                if not self._db_exists_name(name):
                    self.cs.execute(f'INSERT INTO player VALUES ("{name}", NULL, NULL, NULL)')
                    print("    Player {} inserted into table player".format(name))
            except Exception as e:
                print(e)
        self.conn.commit()

    def _db_insert_refid(self, refid, players):
        try:
            if not self._db_exists_refid(refid) and len(players) > 3:
                self.cs.execute(f"INSERT INTO refids VALUES ('{refid}', '{players[0]}', '{players[1]}', '{players[2]}', '{players[3]}')")
                print("   Refid {} - {} inserted into table refids".format(refid, players))
            self.conn.commit()
        except Exception as e:
            print(e)

    def _db_insert_log(self, refid, log):
        try:
            if not self._db_exists_game_log(refid):
                log = str(log).replace("'", "\"")
                self.cs.execute(f"INSERT INTO logs VALUES ('{refid}', '{log}')")
                print("Game log of {} crawled and inserted into TABLE logs.".format(refid))
                self.conn.commit()
        except Exception as e:
            print(e)

    def _db_update_player_level(self, name, level, pt):
        try:
            lv = self.level_dict[level]
            self.cs.execute(f"UPDATE player SET level = '{level}', pt = '{pt}', lv = '{lv}' WHERE name = '{name}'")
            self.conn.commit()
            print("    Player {}'s level-{} and pt-{} is updated.".format(name, level, pt))
        except Exception as e:
            print(e)

    def _db_update_retrieved(self, name):
        try:
            self.cs.execute(f"UPDATE player SET retrieved = TRUE WHERE name = '{name}'")
            self.conn.commit()
            print("    Player {}'s playing history was totally retrieved".format(name))
        except Exception as e:
            print(e)

    def _db_update_unretrieved(self, name):
        try:
            self.cs.execute(f"UPDATE player SET retrieved = NULL WHERE name = '{name}'")
            self.conn.commit()
        except Exception as e:
            print(e)

    def _db_select_players_lv_gr(self, level):
        if True:
            names = self.cs.execute(f"SELECT name FROM player WHERE (retrieved IS NULL AND lv > {level}) ORDER BY lv DESC")
            names = names.fetchall()
            for n in names:
                yield n[0]

    def _db_select_players_no_lv(self):
        need_level_names_cs_obj = self.cs.execute("SELECT name FROM player WHERE level IS NULL")
        names = need_level_names_cs_obj.fetchall()
        for n in names:
            yield n[0]

    def _db_select_refids_no_logs_where_players_lv_gr(self, gr_lv):
        res = self.cs.execute(f"SELECT DISTINCT refids.ref "
                              f"FROM player JOIN refids "
                              f"ON (player.name = refids.p1 OR player.name = refids.p2 "
                              f"OR player.name = refids.p3 OR player.name = refids.p4) "
                              f"WHERE player.lv > {gr_lv} "
                              f"ORDER BY refids.ref DESC")
        for r in res.fetchall():
            if not self._db_exists_game_log(r[0]):
                yield r[0]

    def _db_select_refids_with_logs_where_players_lv_gr(self, gr_lv):
        res = self.cs.execute(f"SELECT DISTINCT refids.ref "
                              f"FROM player JOIN refids "
                              f"ON (player.name = refids.p1 OR player.name = refids.p2 "
                              f"OR player.name = refids.p3 OR player.name = refids.p4) "
                              f"WHERE player.lv > {gr_lv} "
                              f"ORDER BY refids.ref DESC")
        for r in res.fetchall():
            if self._db_exists_game_log(r[0]):
                yield r[0]

    @staticmethod
    def _crawl_get_self_page(name):
        url = "http://arcturus.su/tenhou/ranking/ranking.pl?name=" + name
        agent = "Mozilla/5.0 (Macintosh; Intel ...) Gecko/20100101 Firefox/58.0"
        headers = {'User-Agent': agent}
        r = requests.get(url, headers=headers)
        return r.text

    def _crawl_level_and_pt_by_name(self, name=None, page=None):
        if page:
            text = page
        else:
            if name:
                text = GameLogCrawler._crawl_get_self_page(name)
            else:
                return
        pos1 = str.find(text, 'rank estimation [translateme]')
        pos2 = str.find(text, '[to be generalised] hourly gameplay')
        stats = text[pos1:pos2]
        start = str.find(stats, "4man [translateme]:")
        end = str.find(stats, "<br>")
        fourman = stats[start + 20:end]
        if len(fourman) > 0 and len(fourman.split(" ")) > 1:
            # print(name + ": " + fourman)
            level, pt = fourman.split(" ")
            return level, pt

    def _crawl_refid_and_players_by_name(self, name):
        r = GameLogCrawler._crawl_get_self_page(name)

        level, pt = self._crawl_level_and_pt_by_name(page=str(r))
        if level and pt:
            self._db_update_player_level(name, level, pt)

        soup = bs4.BeautifulSoup(r, 'html.parser')
        rec = soup.find(id="records")
        for l in str(rec).splitlines():
            if "<a href=" in l:
                refid = l[l.find("<a href=") + 34:l.find('">log</a>')]
                names = [n.split('(')[0] for n in l[l.find("</abbr>") + 10:l.find("<br/>")].split(" ")]
                yield {"ref": refid, "players": names}

    def _crawl_log_by_refid(self, refid):
        url = "http://tenhou.net/5/mjlog2json.cgi?" + refid
        referer = "http://tenhou.net/5/?log=" + refid
        agent = "Mozilla/5.0 (Macintosh; Intel ...) Gecko/20100101 Firefox/58.0"
        host = "tenhou.net"
        headers = {'User-Agent': agent, 'Host': host, 'Referer': referer}
        response = requests.get(url, headers=headers).content
        log = json.loads(response)
        return log
        # s = str(fixtures).replace("'", "\"")
        # self.cs.execute(f"INSERT INTO logs VALUES ('{refid}', '{s}')")

    def batch_crawl_refids(self, gr_level, ite=5):
        """
        Crawl multiple game log referal ids and insert them into database.
        It will select players from database that havn't been processed yet,
        and then crawl referal ids of games that the specific player was involed in,
        and finally insert them into database
        :param gr_level: Indicates that crawling will be only processed on players who has a level greater than gr_level
        :param ite: number of iterations
        :return: None
        """
        names_generator = self._db_select_players_lv_gr(gr_level)
        for i in range(ite):
            try:
                current_name = names_generator.__next__()
                refid_generator = self._crawl_refid_and_players_by_name(current_name)
                for refid_item in refid_generator:
                    refid, names = refid_item["ref"], refid_item["players"]
                    self._db_insert_refid(refid, names)
                self._db_update_retrieved(current_name)
            except StopIteration:
                print("    There are not so many ({}) players that have levels greater than {}".format(ite, gr_level))
                print("    Please crawl by smaller gr_level next time or firstly call_batch_crawl_levels()")
                break

    def batch_crawl_levels(self, ite=5):
        """
        Crawl level of players and store them into database.
        It will select players in database that have no level information and update their levels
        :param ite: number of iterations.
        :return: None
        """
        names_no_levels_generator = self._db_select_players_no_lv()
        for i in range(ite):
            try:
                current_name = names_no_levels_generator.__next__()
                level, pt = self._crawl_level_and_pt_by_name(current_name)
                if level and pt:
                    self._db_update_player_level(current_name, level, pt)
            except StopIteration:
                print("All names in TABLE player has now levels!")
                break

    def batch_crawl_logs(self, gr_lv, ite=10):
        """
        Crawl game logs and insert them into database.
        It will firstly select a couple of players whose level is higher than gr_lv,
        then select all referal ids of these players,
        finally game logs of these referal ids will be crawled and stored into database.
        :param gr_lv: a level number, 20 highest, 0 lowest
        :param ite: number of iteration
        :return: None
        """
        gene = self._db_select_refids_no_logs_where_players_lv_gr(gr_lv)
        for i in range(ite):
            try:
                refid = gene.__next__()
                log = self._crawl_log_by_refid(refid)
                self._db_insert_log(refid, log)
            except StopIteration:
                print("All refids have been processed!")
                break

    def db_get_logs_where_players_lv_gr(self, gr_lv):
        """
        Select game logs of players whose level is higher than gr_lv.
        :param gr_lv: level, highest 20, lowest 0
        :return: a generator of game logs that satisfy the constraint
        """
        gene = self._db_select_refids_with_logs_where_players_lv_gr(gr_lv)
        i = 0
        while True:
            try:
                refid = gene.__next__()
                res = self.cs.execute(f"SELECT log FROM logs WHERE refid='{refid}'")
                res = res.fetchone()
                log = res[0]
                log = json.loads(log)
                i += 1
                yield log
            except StopIteration:
                print("All {} logs with players greater than level {} are processed.".format(i, gr_lv))
                break

    @staticmethod
    def prt_log_format(log):
        """
        Print a game log in user friendly format
        :param log: the log dict
        :return: None
        """
        for k, v in log.items():
            if k == 'log':
                print("log:")
                for vv in v:
                    print("    Round {}".format(v.index(vv)))
                    for vvv in vv:
                        print("        {}".format(vvv))
            else:
                print("{}: {}".format(k, v))


class PreProcessing:

    class PlayerState:

        def __init__(self):
            self.name, self.dan, self.score = None, None, None
            self.s_hand34, self.s_meld34, self.s_discard34 = None, None, None
            self.s_minkan, self.s_ankan = None, None
            self.s_red_fives = None
            self.s_player_wind, self.s_round_wind = None, None
            self.s_reach = None
            self.s_bonus_tiles_34 = None
            self.s_opponents = None
            self.s_revealed = None
            self.a_last_action = None
            self.a_action = None
            self.a_result = None

        def init_state(self, hand34, bonus_tiles34, player_wind, round_wind, revealed, name, dan, score):
            self.name, self.dan, self.score = name, dan, score
            self.s_hand34 = hand34
            self.s_red_fives = []
            self.s_meld34, self.s_minkan, self.s_ankan = [], [], []
            self.s_discard34 = []
            self.s_player_wind = player_wind
            self.s_round_wind = round_wind
            self.s_reach = False
            self.s_bonus_tiles_34 = bonus_tiles34
            self.s_revealed = revealed

        def __str__(self):
            str_form = []
            str_form.append("    Player: {}, {}, {}\n".format(self.name, self.dan, self.score))
            str_form.append("    State:\n")
            hands = "        Hand:{}".format(self.s_hand34)
            hands += " + {}".format(self.s_meld34) if len(self.s_meld34) > 0 else ""
            hands += " + {}".format(self.s_minkan) if len(self.s_minkan) > 0 else ""
            hands += " + {}".format(self.s_ankan) if len(self.s_ankan) > 0 else ""
            hands += "\n"
            str_form.append(hands)
            str_form.append("        Discard: {}\n".format(self.s_discard34))
            str_form.append("        Status: Reach {}, Player wind {}, Round wind {}, Red fives {}, "
                            "Bonus tiles {}\n".format(self.s_reach, self.s_player_wind, self.s_round_wind,
                                                      self.s_red_fives, self.s_bonus_tiles_34))
            str_form.append("        Revealed: {}\n".format(self.s_revealed))
            str_form.append("    Last action: {}\n".format(self.a_last_action))
            str_form.append("    Action: {}\n".format(self.a_action))
            str_form.append("    Result: {}\n".format(self.a_result))
            return "".join(str_form)

        def is_winning(self, final_tile, is_zimo):
            partitions = WinWaitCal.win_parse(self.s_hand34, final_tile)
            for p in partitions:
                han = WinWaitCal.han_calculation(p, final_tile, self.s_meld34, self.s_minkan, self.s_ankan,
                                                 is_zimo, self.s_player_wind, self.s_round_wind, self.s_reach)
                if han["han_sum"] > 0 or han["yk_sum"] > 0:
                    return True
            return False

    @staticmethod
    def process_one_round(log, names, dans):
        if log[16][0] == '九種九牌':
            return ['九種九牌']
        else:
            res = []
            round_num = log[0][0]
            round_scores = [0, 0, 0, 0] if len(log[16]) < 2 else log[16][1]
            bonus_tiles, bonus_indicators, bonus_to = [], log[2], 1
            first_indicator_34 = Tile.his_to_34(bonus_indicators[0])
            first_bonus = Tile.bns_ind_bd_dic.get(first_indicator_34, first_indicator_34 + 1)
            bonus_tiles.append(first_bonus)
            round_wind = Tile.WINDS[round_num // 4]
            player_winds = Tile.WINDS[round_num:] + Tile.WINDS[0:round_num]
            revealed = [0] * 34

            states = [PreProcessing.PlayerState(), PreProcessing.PlayerState(),
                      PreProcessing.PlayerState(), PreProcessing.PlayerState()]
            for player in range(0, 4):  # 4,7,10,13
                base_index = (player + 1) * 3
                initial_hand_index = base_index + 1
                hand34 = Tile.his_to_34(log[initial_hand_index])
                states[player].s_red_fives = [Tile.his_to_34(t) for t in log[initial_hand_index] if t > 50]
                states[player].init_state(hand34, bonus_tiles, player_winds[player],
                                          round_wind, revealed, names[player], dans[player], log[1][player])

            current_player = round_num % 4
            drop_to = [0, 0, 0, 0]
            draw_to = [0, 0, 0, 0]

            def pack_opps(current_player):
                opps = []
                for i in range(1, 4):
                    opp = (current_player + i) % 4
                    opp = deepcopy(states[opp])
                    opp.s_opponents = None
                    opps.append(opp)
                return opps

            while current_player != -1:
                base_index = (current_player + 1) * 3
                draw_index, drop_index = base_index + 2, base_index + 3
                # handle drawn tile
                draw = log[draw_index][draw_to[current_player]]
                is_draw_string = isinstance(draw, str)

                if not is_draw_string:
                    if states[current_player].is_winning(Tile.his_to_34(draw), True):
                        if (draw_to[current_player] + 1) == len(log[draw_index]):
                            states[current_player].a_last_action = {"type": "draw", "tile": Tile.his_to_34(draw)}
                            final_score = round_scores[current_player:] + round_scores[0:current_player]
                            states[current_player].a_action = {"type": "zimo", "score": final_score}
                            states[current_player].a_result = {"type": "win", "score": final_score}
                            states[current_player].s_opponents = pack_opps(current_player)
                            res.append(deepcopy(states[current_player]))
                            break
                    draw34 = Tile.his_to_34(draw)
                    states[current_player].s_hand34.append(draw34)

                if is_draw_string:
                    if 'p' in draw:
                        which = draw.index('p') // 2
                        draw = draw.replace('p', '')
                        pons = [Tile.his_to_34(int(draw[i*2:(i+1)*2])) for i in range(3)]
                        states[current_player].a_last_action = {"type": "opp_drop", "tile": pons[0]}
                        states[current_player].a_action = {"type": "pon", "tile": pons[0]}
                        states[current_player].a_result = None
                        states[current_player].s_opponents = pack_opps(current_player)
                        res.append(deepcopy(states[current_player]))
                        for i in range(0, 3):
                            if i != which:
                                states[current_player].s_hand34.remove(pons[i])
                        states[current_player].s_meld34.append(pons)
                        revealed[pons[0]] += 2
                    if 'c' in draw:
                        chow1 = Tile.his_to_34(int(draw[1:3]))
                        chow2 = Tile.his_to_34(int(draw[3:5]))
                        chow3 = Tile.his_to_34(int(draw[5:7]))
                        states[current_player].a_last_action = {"type": "opp_drop", "tile": chow1}
                        states[current_player].a_action = {"type": "chow", "tile": chow1}
                        states[current_player].a_result = None
                        states[current_player].s_opponents = pack_opps(current_player)
                        res.append(deepcopy(states[current_player]))
                        states[current_player].s_hand34.remove(chow2)
                        states[current_player].s_hand34.remove(chow3)
                        chow = sorted([chow1, chow2, chow3])
                        states[current_player].s_meld34.append(chow)
                        revealed[chow2] += 1
                        revealed[chow3] += 1
                    if 'm' in draw:
                        which = draw.index('m') // 2
                        draw = draw.replace('m', '')
                        kans = [Tile.his_to_34(int(draw[i*2:(i+1)*2])) for i in range(4)]
                        states[current_player].a_last_action = {"type": "draw", "tile": kans[0]}
                        states[current_player].a_action = {"type": "minkan", "tile": kans[0]}
                        states[current_player].a_result = None
                        states[current_player].s_opponents = pack_opps(current_player)
                        res.append(deepcopy(states[current_player]))
                        for i in range(0, 4):
                            if i != which:
                                states[current_player].s_hand34.remove(kans[i])
                        states[current_player].s_minkan.append(kans)
                        revealed[kans[0]] += 3
                        draw_to[current_player] += 1
                        drop_to[current_player] += 1
                        if bonus_to < len(bonus_indicators):
                            indicator = Tile.his_to_34([bonus_indicators[bonus_to]])
                            bonus_to += 1
                            bonus_tiles.append(Tile.bns_ind_bd_dic.get(indicator, indicator + 1))
                        continue

                drop = log[drop_index][drop_to[current_player]]
                is_drop_string = isinstance(drop, str)

                if not is_drop_string:
                    drop = draw if drop == 60 else drop
                    drop34 = Tile.his_to_34(drop)
                    for i in range(1, 4):
                        ck_player = (current_player + i) % 4
                        if states[ck_player].is_winning(drop34, False):
                            if (drop_to[current_player] + 1) == len(log[drop_index]):
                                states[current_player].a_last_action = None
                                states[current_player].a_action = {"type": "drop", "tile": drop34}
                                states[current_player].a_result = {"type": "lose", "tile": drop34}
                                states[current_player].s_opponents = pack_opps(current_player)
                                res.append(deepcopy(states[current_player]))
                                break

                was_reach_drop = False
                if is_drop_string:
                    if 'a' in drop:
                        drop = drop.replace('a', '')
                        kans = [Tile.his_to_34(int(drop[i*2:(i+1)*2])) for i in range(4)]
                        states[current_player].a_last_action = {"type": "draw", "tile": kans[0]}
                        states[current_player].a_action = {"type": "ankan", "tile": kans[0]}
                        states[current_player].a_result = None
                        states[current_player].s_opponents = pack_opps(current_player)
                        res.append(deepcopy(states[current_player]))
                        for k in kans:
                            states[current_player].s_hand34.remove(k)
                        states[current_player].s_ankan.append(kans)
                        revealed[kans[0]] += 4
                        draw_to[current_player] += 1
                        drop_to[current_player] += 1
                        if bonus_to < len(bonus_indicators):
                            indicator = Tile.his_to_34([bonus_indicators[bonus_to]])
                            bonus_to += 1
                            bonus_tiles.append(Tile.bns_ind_bd_dic.get(indicator, indicator + 1))
                        continue
                    if 'k' in drop:
                        which = drop.index('k') // 2
                        old_pon, new_drawn = [], None
                        drop = drop.replace('k', '')
                        kans = [Tile.his_to_34(int(drop[i * 2:(i + 1) * 2])) for i in range(4)]
                        for i in range(1, 4):
                            ck_player = (current_player + i) % 4
                            if states[ck_player].is_winning(kans[0], True):
                                states[current_player].a_last_action = {"type": "draw", "tile": kans[0]}
                                states[current_player].a_action = {"type": "chakan", "tile": kans[0]}
                                states[current_player].a_result = {"type": "lose", "tile": kans[0], "score": round_scores[current_player], "who_wins": ck_player}
                                states[current_player].s_opponents = pack_opps(current_player)
                                res.append(deepcopy(states[current_player]))
                                break
                        states[current_player].a_last_action = {"type": "draw", "tile": kans[0]}
                        states[current_player].a_action = {"type": "chakan", "tile": kans[0]}
                        states[current_player].a_result = None
                        states[current_player].s_opponents = pack_opps(current_player)
                        res.append(deepcopy(states[current_player]))

                        states[current_player].s_meld34.remove(kans[0:3])
                        states[current_player].s_minkan.append(kans)
                        states[current_player].s_hand34.remove(kans[0])

                        revealed[kans[0]] += 1
                        draw_to[current_player] += 1
                        drop_to[current_player] += 1
                        if bonus_to < len(bonus_indicators):
                            indicator = Tile.his_to_34([bonus_indicators[bonus_to]])
                            bonus_to += 1
                            bonus_tiles.append(Tile.bns_ind_bd_dic.get(indicator, indicator + 1))
                        continue
                    if 'r' in drop:
                        states[current_player].s_reach = True
                        drop = int(drop[1:3])
                        drop = draw if drop == 60 else drop
                        drop34 = Tile.his_to_34(drop)
                        for i in range(1, 4):
                            ck_player = (current_player + i) % 4
                            if states[ck_player].is_winning(drop34, False):
                                if (drop[current_player] + 1) == len(log[drop_index]):
                                    states[current_player].a_last_action = states[current_player].a_action
                                    states[current_player].a_action = {"type": "reach_drop", "tile": drop34}
                                    states[current_player].a_result = {"type": "lose", "tile": drop34}
                                    states[current_player].s_opponents = pack_opps(current_player)
                                    res.append(deepcopy(states[current_player]))
                                    break
                        states[current_player].a_last_action = states[current_player].a_action
                        states[current_player].a_action = {"type": "reach_drop", "tile": drop34}
                        states[current_player].a_result = None
                        states[current_player].s_opponents = pack_opps(current_player)
                        res.append(deepcopy(states[current_player]))
                        was_reach_drop = True

                drop = draw if drop == 60 else drop
                drop34 = Tile.his_to_34(drop)

                if not was_reach_drop:
                    states[current_player].a_last_action = states[current_player].a_action
                    states[current_player].a_action = {"type": "drop", "tile": drop34}
                    states[current_player].a_result = None
                    states[current_player].s_opponents = pack_opps(current_player)
                    res.append(deepcopy(states[current_player]))

                states[current_player].s_hand34.remove(drop34)
                states[current_player].s_hand34.sort()
                draw_to[current_player] += 1
                drop_to[current_player] += 1
                states[current_player].s_discard34.append(drop34)
                revealed[drop34] += 1

                if all(draw_to[cp] >= len(log[(cp + 1) * 3 + 2])
                       for cp in [(current_player + i) % 4 for i in range(1, 4)]):
                    # print("流局")
                    for i in range(0, 4):
                        states[current_player].a_last_action = states[current_player].a_action
                        states[current_player].a_action = None
                        states[current_player].a_result = {"type": "liuju"}
                        states[current_player].s_opponents = pack_opps(current_player)
                        res.append(deepcopy(states[current_player]))
                    return res

                for i in range(1, 4):
                    check_player = (current_player + i) % 4
                    draw_index = (check_player + 1) * 3 + 2
                    if draw_to[check_player] >= len(log[draw_index]):
                        continue
                    drew = log[draw_index][draw_to[check_player]]
                    if isinstance(drew, str) and 'c' in drew and str(drop) == drew[1:3]:
                        if check_player == (current_player + 1) % 4:
                            current_player = check_player
                            break
                    if isinstance(drew, str) and 'p' in drew:
                        which = drew.index('p') // 2
                        drew = drew.replace('p', '')
                        pons = [int(drew[i * 2:(i + 1) * 2]) for i in range(0, 3)]
                        if drop in pons and which == (i - 1):
                            current_player = check_player
                            break
                    if isinstance(drew, str) and 'm' in drew:
                        drew = drew.replace('m', '')
                        kans = [int(drew[i * 2:(i + 1) * 2]) for i in range(0, 4)]
                        if drop in kans:
                            current_player = check_player
                            break
                else:
                    current_player = (current_player + 1) % 4

            return res

    @staticmethod
    def process_one_log(log):
        """
        Pre-process one log file
        :param log: game log as a dict
        :return: res dict, key=round number, value=sequences of state action pairs
        """
        names, dans = log['name'], log['dan']
        res = {}
        rounds = log['log']
        for i in range(len(rounds)):
            res[i+1] = PreProcessing.process_one_round(rounds[i], names, dans)
        return res


def main():
    glc = GameLogCrawler()
    gene = glc.db_get_logs_where_players_lv_gr(19)
    log = gene.__next__()
    res = PreProcessing.process_one_log(log)
    for k, v in res.items():
        print("Round {}".format(k))
        for state in v:
            print(state)


if __name__ == '__main__':
    main()