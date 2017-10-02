import pifacecad
from threading import Thread, Barrier


class MediaPlayerPiFaceCAD:
    def __init__(self, media_player):
        self._cad = pifacecad.PiFaceCAD()
        self._media_player = media_player
        self._switch_listener = pifacecad.SwitchEventListener()

        # https://github.com/piface/pifacedigitalio/issues/27
        self._switch_listener_barrier = Barrier(2)
        self._switch_listener_wait_for_deactivation_thread = Thread(target=self._switch_listener_wait_for_deactivation,
                                                                    args=[])
        self._switch_listener_wait_for_deactivation_thread.setDaemon(True)
        self._switch_listener_wait_for_deactivation_thread.start()

        self._switch_listener.register(0, pifacecad.IODIR_ON,
                                       lambda event: self._clear_and_call(media_player.prev_track))
        self._switch_listener.register(1, pifacecad.IODIR_ON,
                                       lambda event: media_player.play())
        self._switch_listener.register(2, pifacecad.IODIR_ON,
                                       lambda event: media_player.pause())
        self._switch_listener.register(3, pifacecad.IODIR_ON,
                                       lambda event: self._clear_and_call(media_player.next_track))
        self._switch_listener.register(4, pifacecad.IODIR_ON,
                                       lambda event: self._stop(media_player))
        self._switch_listener.register(6, pifacecad.IODIR_ON,
                                       lambda event: self._clear_and_call(media_player.prev_track))
        self._switch_listener.register(7, pifacecad.IODIR_ON,
                                       lambda event: self._clear_and_call(media_player.next_track))
        self._switch_listener.activate()
        self._cad.lcd.blink_off()
        self._cad.lcd.cursor_off()
        self._cad.lcd.clear()
        self._cad.lcd.backlight_on()
        self._cad.lcd.write('Waiting for CD')

    def _switch_listener_wait_for_deactivation(self):
        try:
            self._switch_listener_barrier.wait()
        except:
            pass  # expected reset
        self._switch_listener.deactivate()

    def _clear_and_call(self, func):
        self._cad.lcd.clear()
        func()

    def _stop(self, media_player):
        media_player.stop()
        self.destroy()

    def destroy(self):
        self._cad.lcd.clear()
        self._cad.lcd.backlight_off()
        self._switch_listener_barrier.reset()  # should never wait

    def write_info(self, media_player_info):
        if media_player_info.status == 'paused':
            self._cad.lcd.home()
            self._cad.lcd.write('Paused          ')
        elif media_player_info.status == 'waitingForCD':
            self._cad.lcd.clear()
            self._cad.lcd.write('Waiting for CD')
        elif media_player_info.status == 'playing' and media_player_info.cur_track_info is not None:
            self._cad.lcd.home()
            if media_player_info.cur_track_info.track_number is not None:
                track_list = self._media_player.current_track_list
                total_tracks = len(track_list)
                cur_track = media_player_info.cur_track_info.track_number + 1
                track_str_len = len(str(cur_track)) + len(str(total_tracks)) + 1
                self._cad.lcd.set_cursor(16 - track_str_len, 1)
                self._cad.lcd.write(str(cur_track) + '/' + str(total_tracks))