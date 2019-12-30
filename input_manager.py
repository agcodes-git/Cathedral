# A pair of dictionaries mapping strings to booleans.
# Strings can be anything, but typically map to keyboard keys.
import copy, pygame, sys

last_keys_down = {}
keys_down = {}
mouse_position = (0,0)
axes = {}
hats = {}

left = [0]
right = [0]

down = (lambda key: str(key) in keys_down and keys_down[str(key)])
pressed = (lambda key: (str(key) in keys_down and keys_down[str(key)]) and (str(key) not in last_keys_down or (str(key) in last_keys_down and not last_keys_down[str(key)])))
released = (lambda key: (str(key) in keys_down and not keys_down[str(key)]) and (str(key) in last_keys_down and last_keys_down[str(key)]))

scroll_direction = 0

def update_inputs( events, debug=False ):

    global scroll_direction
    global last_keys_down
    global mouse_position

    scroll_direction = 0
    last_keys_down = copy.deepcopy( keys_down )
    for event in events:
        if event.type == pygame.QUIT: sys.exit()
        elif event.type == pygame.KEYDOWN:
            keys_down[str(event.key)] = True
        elif event.type == pygame.KEYUP:
            keys_down[str(event.key)] = False
        elif event.type == pygame.MOUSEMOTION:
            mouse_position = event.pos
        elif event.type == pygame.MOUSEBUTTONDOWN:
            keys_down['mb'+str(event.button)] = True
            if event.button == 4: scroll_direction = 1
            if event.button == 5: scroll_direction = -1

        elif event.type == pygame.MOUSEBUTTONUP:
            keys_down['mb'+str(event.button)] = False
        elif event.type == pygame.JOYBUTTONDOWN:
            keys_down['bt'+str(event.joy)+str(event.button)] = True
        elif event.type == pygame.JOYBUTTONUP:
            keys_down['bt'+str(event.joy)+str(event.button)] = False
        elif event.type == pygame.JOYAXISMOTION:
            axes['ax'+str(event.joy)+str(event.axis)] = event.value
        elif event.type == pygame.JOYHATMOTION:
            hats['ht'+str(event.joy)+str(event.hat)] = event.value
            keys_down['ht' + str(event.joy) + str(event.hat) + '_left'] = event.value[0] == -1
            keys_down['ht' + str(event.joy) + str(event.hat) + '_right'] = event.value[0] == 1
            keys_down['ht' + str(event.joy) + str(event.hat) + '_down'] = event.value[1] == -1
            keys_down['ht' + str(event.joy) + str(event.hat) + '_up'] = event.value[1] == 1

        if debug and event.type != pygame.MOUSEMOTION: print(event)

