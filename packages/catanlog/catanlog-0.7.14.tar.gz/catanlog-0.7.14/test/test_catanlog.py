import hexgrid
from nose.tools import assert_regexp_matches
import catanlog
from catan.game import Player


syntax = {
    'header': '',
    'roll': r'[a-z]+ rolls \d{1,2}',
    'robber': r'[a-z]+ moves robber to \d{1,2}, steals from [a-z]+',
    'buy': r'[a-z]+ buys (road|settlement|city|dev card)(, builds at \(\d{1,2} [NSEW]{1,2}\))?'
}


class TestCatanLog(object):

    @staticmethod
    def output_of(method, *args, **kwargs):
        log = catanlog.CatanLog(auto_flush=True, log_dir='test/tmp', use_stdout=False)
        method(log, *args, **kwargs)
        lines = []
        with open(log.logpath(), 'r') as fp:
            lines.append(fp.readline())
        return lines

    def test_header(self):
        pass

    def test_roll(self):
        player = Player(1, 'ross', 'red')
        for roll in range(2, 12+1):
            assert_regexp_matches(self.output_of(catanlog.CatanLog.log_player_roll, player, roll), syntax['roll'])

    def test_move_robber(self):
        player = Player(1, 'ross', 'red')
        victim = Player(2, 'josh', 'yellow')
        for tile_id in range(1, 19+1):
            assert_regexp_matches(self.output_of(catanlog.CatanLog.log_player_moves_robber_and_steals, player, tile_id, victim), syntax['robber'])

    def test_buy_build(self):
        player = Player(1, 'ross', 'red')
        node = hexgrid.nodes_touching_tile(hexgrid.legal_tile_ids()[0])[0]
        edge = hexgrid.edges_touching_tile(hexgrid.legal_tile_ids()[0])[0]

        output = self.output_of(catanlog.CatanLog.log_player_buys_settlement, player, node)

    def test_trading_with_players(self):
        pass

    def test_trading_with_ports(self):
        pass

    def test_playing_dev_cards(self):
        pass

    def test_end_turn(self):
        pass

    def test_end_game(self):
        pass


