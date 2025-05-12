import os
import replayparser as gzr
from replayparser.models import (
    AntileadShotgun,
    GameDead,
    MMatchRoundResult,
    MMatchRoundState,
    MMatchWeaponType,
    Round,
    HPAPInfo,
    ChangeWeapon,
    Dash,
    Slash,
    Reload,
    PeerShotSP,
    PeerSPMotion,
    Spawn,
    Announcement,
    Skill,
    Massive,
    Death,
    WorldItemPickup
)
from replayparser.util.basicinfo import BasicInfo

def muid_to_name(r, muid):
    for player in r.players:
        if player.muid == muid:
            return player.name
    return f"Unknown_Player({muid})"


damage_by_round = {1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}, 7: {}}
def entry():
    replay = gzr.parse_replay(f"assets/igz_ladder.gzr")
    current_round = 1
    for sender, packet in replay.packets:
        pt = type(packet)
        if pt == BasicInfo:
            pass
        elif pt == GameDead:
            str_attacker = muid_to_name(replay, packet.attacker)
            str_victim = muid_to_name(replay, packet.victim)
            str_weapon = MMatchWeaponType(packet.weapon_type).name
            print(f"{current_round}: {str_attacker} killed {str_victim} with {str_weapon}")
        elif pt == AntileadShotgun:
            str_attacker = muid_to_name(replay, sender)
            if packet.hit:
                damage = packet.damage
                if str_attacker not in damage_by_round[current_round]:
                    damage_by_round[current_round][str_attacker] = 0
                damage_by_round[current_round][str_attacker] += damage
            else:
                print(f"{current_round}: {str_attacker} missed")
        elif pt == Round:
            pass
            if MMatchRoundState(packet.state) == MMatchRoundState.MMATCH_ROUNDSTATE_PLAY:
                print("=" * 50)
                print(f"Round {packet.round} started")
                current_round += 1
            elif MMatchRoundState(packet.state) == MMatchRoundState.MMATCH_ROUNDSTATE_FINISH:
                if MMatchRoundResult(packet.arg) == MMatchRoundResult.DRAW:
                    print(f"Round {packet.round + 1} ended in a draw")
                elif MMatchRoundResult(packet.arg) == MMatchRoundResult.BLUE_WIN:
                    print(f"Round {packet.round + 1} ended, Blue team wins")
                elif MMatchRoundResult(packet.arg) == MMatchRoundResult.RED_WIN:
                    print(f"Round {packet.round + 1} ended, Red team wins")
        elif pt == HPAPInfo:
            pass
        elif pt == ChangeWeapon:
            pass
        elif pt == Dash:
            pass
        elif pt == Slash:
            pass
        elif pt == Reload:
            pass
        elif pt == PeerShotSP:
            pass
        elif pt == PeerSPMotion:
            pass
        elif pt == Spawn:
            pass
        elif pt == Announcement:
            pass
        elif pt == Skill:
            pass
        elif pt == Massive:
            str_attacker = muid_to_name(replay, sender)
            print(f"{current_round}: {str_attacker} threw a massive")
        elif pt == Death:
            pass
        elif pt == WorldItemPickup:
            pass

if __name__ == "__main__":
    entry()
    for round in damage_by_round:
        print(f"Round {round}:")
        for player, damage in damage_by_round[round].items():
            print(f"{player}: {damage} damage")