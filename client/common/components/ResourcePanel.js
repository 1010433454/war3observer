import * as m from 'mithril';
import { getPlayerColor } from '../utils/color';
import Component from '../Component';
import Resource from './Resource';

export default class ResourcePanel extends Component {
  view(vnode) {
    const { player, icons={} } = vnode.attrs;
    const type = player.race.toLowerCase();

    return (
      <div class={`ResourcePanel ResourcePanel--${type}`}>
        <Resource
          icon={icons[player.race.toLowerCase()]}
          class={`color-${getPlayerColor(player)}`}>
          {player.name}
        </Resource>

        <Resource icon={icons.gold}>
          {player.gold}
        </Resource>

        <Resource icon={icons.lumber}>
          {player.lumber}
        </Resource>

        <Resource icon={icons.supply}>
          {player.food}/{player.food_max}
        </Resource>
      </div>
    );
  }
}
