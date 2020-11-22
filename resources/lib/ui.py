import os
import xbmcgui
import xbmcaddon
import pyxbmct

import bridge
from tools import notify, xbmclog

_addon = xbmcaddon.Addon()
_addon_path = _addon.getAddonInfo('path')

class Entertainment(pyxbmct.AddonDialogWindow):
    def __init__(self, title, lights_items, lights_ids, config):
        super(Entertainment, self).__init__(title)
        screenx = self.getWidth()
        screeny = self.getHeight()
        xbmclog('Screen resolution: {}x{}'.format(screenx, screeny))
        self.config = config
        self.available_lights = lights_items
        self.lights_ids = lights_ids
        self.save_new_configuration = False
        self.setGeometry(800, 600, 20, 20)
        self.set_controls()

    def set_controls(self):
        self.light_control_list = pyxbmct.List('font14')
        self.placeControl(self.light_control_list, 0, 0, rowspan=17, columnspan=6)
        self.light_control_list.addItems(self.available_lights)
        self.connect(self.light_control_list, self.display_lights_configuration)
        self.save_button = pyxbmct.Button('Save')
        self.placeControl(self.save_button, 17, 0, rowspan=2, columnspan=6)
        self.close_button = pyxbmct.Button('Close')
        self.placeControl(self.close_button, 17, 14, rowspan=2, columnspan=6)
        self.connect(self.close_button, self.close)
        self.connect(self.save_button, self.save)


        self.placeControl(pyxbmct.Label('X:'), 0, 6)
        self.sliderX = pyxbmct.Slider()
        self.placeControl(self.sliderX, 0, 7, columnspan=4)
        self.sliderX_value = pyxbmct.Label('0', alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(self.sliderX_value, 1, 7, columnspan=4)        

        self.placeControl(pyxbmct.Label('Y:'), 0, 13)
        self.sliderY = pyxbmct.Slider()
        
        self.placeControl(self.sliderY, 0, 14, columnspan=4)
        self.sliderY_value = pyxbmct.Label('0', alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(self.sliderY_value, 1, 14, columnspan=4)

        self.connectEventList([pyxbmct.ACTION_MOVE_LEFT,
                               pyxbmct.ACTION_MOVE_RIGHT,
                               pyxbmct.ACTION_MOUSE_DRAG,
                               pyxbmct.ACTION_MOUSE_LEFT_CLICK],
                              self.slider_update)

        self.image = pyxbmct.Image(os.path.join(_addon_path, 'resources', 'texture', 'mire.png'))
        self.placeControl(self.image, 2, 7, rowspan=14, columnspan=12)
        self.image.setWidth(400)
        self.image.setHeight(400)

        xbmclog('Image size => {}x{}, position {}x{}'.format(self.image.getWidth(), self.image.getHeight(), self.image.getX(), self.image.getY()))

        self.bulb = pyxbmct.Image(os.path.join(_addon_path, 'resources', 'texture', 'bulb.png'))
        self.addControl(self.bulb)
        self.light_control_list.selectItem(0)
        self.display_lights_configuration()

    def save(self):
        xbmclog('Save!')
        self.save_new_configuration = True
        self.close()
    
    def display_lights_configuration(self):
        xbmclog('Lights available => {}'.format(self.available_lights))
        xbmclog('Selected lights => {}'.format(self.light_control_list.getSelectedPosition()))
        xbmclog('Light conf {} => {}'.format(self.light_control_list.getListItem(self.light_control_list.getSelectedPosition()).getLabel(), self.config))
        light_id = self.lights_ids[self.light_control_list.getSelectedPosition()]
        if (not self.config.has_key(light_id)):
            self.config[light_id] = [0.0, 0.0, 0.0] #[x, y, z] z is ignored today

        x = self.image.getX() + (self.image.getWidth() / 2 + (self.image.getWidth() / 2 * self.config[light_id][0])) - 24
        y = self.image.getY() + (self.image.getHeight() / 2 + (self.image.getHeight() / 2 * self.config[light_id][1])) - 24
        xbmclog('Bulb position => {}x{}'.format(x, y))

        self.bulb.setPosition(int(round(x)), int(round(y)))
        self.bulb.setWidth(48)
        self.bulb.setHeight(48)

        self.sliderX.setFloat((self.config[light_id][0] + 1.0 * 50.0), 0.0, 0.05, 100.0)
        self.sliderX_value.setLabel('{:.1F}'.format(self.config[light_id][0]))
        self.sliderY.setFloat((self.config[light_id][1] + 1.0 * 50.0), 0.0, 0.05, 100.0)
        self.sliderY_value.setLabel('{:.1F}'.format(self.config[light_id][1]))

        
        
    def slider_update(self):
         # Update slider value label when the slider nib moves
        light_id = self.lights_ids[self.light_control_list.getSelectedPosition()]
        xbmclog('Light conf {}'.format(self.config[light_id]))
        try:
            if self.getFocus() == self.sliderX:
                value = round((self.sliderX.getFloat() / 50.0) - 1.0, 2)
                xbmclog('X = {}'.format(value))
                self.sliderX_value.setLabel('{:.1F}'.format(value))
                self.config[light_id][0] = value
            elif self.getFocus() == self.sliderY:
                value = round((self.sliderY.getFloat() / 50.0) - 1.0, 2)
                xbmclog('Y = {}'.format(value))
                self.sliderY_value.setLabel('{:.1F}'.format(value))
                self.config[light_id][1] = value
            xbmclog('Light position => {}x{}'.format(self.config[light_id][0], self.config[light_id][1]))
            x = self.image.getX() + (self.image.getWidth() / 2 + (self.image.getWidth() / 2 * self.config[light_id][0])) - 24
            y = self.image.getY() + (self.image.getHeight() / 2 + (self.image.getHeight() / 2 * self.config[light_id][1])) - 24
            self.bulb.setPosition(int(round(x)), int(round(y)))
        except (RuntimeError, SystemError):
            pass
    


def multiselect_lights(bridge_ip, bridge_user, label, exclude,
                       preselect):
    xbmclog('Kodi Hue: In multiselect_lights(bridge_ip={}, bridge_user={}, '
            'label={}, exclude={}, preselect={})'.format(
                bridge_ip, bridge_user, label, exclude, preselect)
            )
    lights = bridge.get_lights_by_ids(bridge_ip, bridge_user)
    actual_lights = []
    items = []
    preselect_items = []
    index = 0
    for light_id, light in lights.items():
        if str(light_id) not in exclude.split(','):
            items.append(xbmcgui.ListItem(label=light.name))
            actual_lights.append(light)
            if str(light_id) in preselect.split(','):
                preselect_items.append(index)
            index += 1

    selected = xbmcgui.Dialog().multiselect(label, items,
                                            preselect=preselect_items)

    if selected:
        light_ids = [str(actual_lights[idx].light_id) for idx in selected]
        return ','.join(light_ids)
    return ''

def configure_entertainment(bridge_ip, bridge_user, label, light_list_id, entertainment_configuration):
    xbmclog('Kodi Hue: In configure_entertainment(bridge_ip={}, bridge_user={}, '
            'label={}, light_list_id={})'.format(
                bridge_ip, bridge_user, label, light_list_id)
            )
    lights_items = []
    lights = bridge.get_lights_by_ids(bridge_ip, bridge_user)
    for light_id, light in lights.items():
        if str(light_id) in light_list_id.split(','):
            xbmclog('Kodi Hue: Item {}'.format(light.name))
            lights_items.append(xbmcgui.ListItem(label=light.name))
    
    addon = Entertainment(label, lights_items, light_list_id.split(','), entertainment_configuration)
    addon.doModal()
    if addon.save_new_configuration:
        xbmclog('Kodi Hue: Save entertainment {}'.format(addon.config))
        to_save = addon.config

    del addon

    if to_save:
        return to_save
    else:
        return None


def discover_hue_bridge(hue):
    notify("Hue Bridge Discovery", "starting")
    hue_ip = bridge.discover()
    if hue_ip is not None:
        notify("Hue Bridge Discovery", "Found bridge at: %s" % hue_ip)
        is_entertainment_compatible = bridge.check_entertainment_compatibility(hue_ip)
        username, userkey = bridge.create_user(hue_ip, is_entertainment_compatible)
        hue.settings.update(bridge_ip=hue_ip)
        hue.settings.update(bridge_user=username)
        hue.settings.update(bridge_key=userkey)
        hue.settings.update(is_entertainment_capable=is_entertainment_compatible)
        hue.settings.update(connected="true")
        hue.connected = True
        notify("Hue Bridge Discovery", "Finished")
    else:
        notify("Hue Bridge Discovery", "Failed. Could not find bridge.")
