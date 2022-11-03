from __future__ import annotations
import datetime
import uuid

from extension.src.pythonpath.core_constants import \
    BTN_SWITCH_TOOLBAR, BTN_DOTTED_UNDERLINE, BTN_CHECK_PAIRS, \
    BTN_SET_FONTS, BTN_COLOR_DIGITS, BTN_CONFIGURE, UI_ELEMENT_LABELS, \
    BTN_INSERT_ACCENT, BUTTONS_NAMES, ButtonData, FOLDER_ICONS, \
    EXTENSION_ID, EXTENSION_VERSION, EXTENSION_NAME, EXTENSION_AUTHOR, EXTENSION_TITLE


def temp_name() -> str:
    return str(uuid.uuid4()).split("-")[0]


DIRECTORY_TEMP_FILES = temp_name()
FOLDER_META_INF = "META-INF"
DEFAULT_OUTPUT_EXTENSION = "oxt"
DEFAULT_ICON_NAME = "icon_extension_logo"
MENU_TITLE = EXTENSION_NAME


def generate_ui_translation_file(language: str) -> str:
    elements = UI_ELEMENT_LABELS.get(language)
    ui_translation_file = "# coding: utf-8\n\n"
    for element, label in elements.items():
        ui_translation_file += f'{element} = "{label}"\n'
    return ui_translation_file


files = {
    "manifest.xml": f"""<?xml version="1.0" encoding="UTF-8"?>
  <manifest:manifest xmlns:manifest="http://openoffice.org/2001/manifest">
  <manifest:file-entry manifest:media-type="application/vnd.sun.star.configuration-data" manifest:full-path="Addons.xcu"/>                     
  <manifest:file-entry manifest:media-type="application/vnd.sun.star.uno-component;type=Python" manifest:full-path="src/interface.py"/>
</manifest:manifest>
""",
    "desc_en.txt": f"© {EXTENSION_AUTHOR}, {datetime.datetime.now().year}",
    "Addons.xcu": f"""<?xml version="1.0" encoding="UTF-8"?>
<oor:component-data xmlns:oor="http://openoffice.org/2001/registry"
                   xmlns:xs="http://www.w3.org/2001/XMLSchema" oor:name="Addons"
                   oor:package="org.openoffice.Office">
    <node oor:name="AddonUI">
        <node oor:name="OfficeMenuBar">
            <node oor:name="{EXTENSION_ID}" oor:op="replace">
                <prop oor:name="Title" oor:type="xs:string">
                    <value/>
                    <value xml:lang="en-US">~{MENU_TITLE}</value>
                </prop>
               <prop oor:name="Target" oor:type="xs:string">
                   <value>_self</value>
               </prop>
               <prop oor:name="ImageIdentifier" oor:type="xs:string">
                   <value/>
               </prop>
        <node oor:name="Submenu">
          <!-- NOTE: Name "N001" will define our order in menu -->
          {ButtonData.generate_submenu_nodes(BUTTONS_NAMES)}
        </node>
      </node>
    </node>

    <node oor:name="Images">
      f"{ButtonData.generate_images_nodes(BUTTONS_NAMES)}"
    </node>
  </node>
</oor:component-data>
""",
    "description.xml": f"""<?xml version="1.0" encoding="UTF-8"?>
<description xmlns="http://openoffice.org/extensions/description/2006"
xmlns:d="http://openoffice.org/extensions/description/2006"
xmlns:xlink="http://www.w3.org/1999/xlink">

  <version value="{EXTENSION_VERSION}" />

  <identifier value="{EXTENSION_ID}" />

  <platform value="all" />

  <dependencies>
    <OpenOffice.org-minimal-version value="3.3" d:name="OpenOffice.org 3.3"/>
  </dependencies>

  <display-name>
    <name lang="en">{EXTENSION_TITLE}</name>
  </display-name>

  <icon>
    <default xlink:href="{FOLDER_ICONS}/{DEFAULT_ICON_NAME}.png" />
    <high-contrast xlink:href="{FOLDER_ICONS}/{DEFAULT_ICON_NAME}.png" />
  </icon>

  <extension-description>
    <src xlink:href="desc_en.txt" lang="en" />
  </extension-description>

</description>""",
}

icons = {
    f"{DEFAULT_ICON_NAME}.png": b'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',
    f"{BTN_COLOR_DIGITS}.png": b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADdcAAA3XAUIom3gAAAL1SURBVEhLrZXPaxNBFMdnZnfzs0nUFn/gX6CCiFhaTH95UtCK3gQpWEH0qBeFXoRe/UHBg4IHhYKggsQeFCvYgy0F8aIHESqilLYYaDWNadLNzjy/u5mmoWmywfQDs/Pe25n57rx5k3AGuu++3uMo4wnBRMBwY7Wguai2KiDA2HvJaPDjSPd3HfUQ7qMojUvo+vwWrwn36DE5v6EjZTwBLJzwvCaRTvFAS6BlXzwe36FDJYGtwv6bTkomvzircjwaje50Y1sqEGxp+4DuLJE6SA71uzFPQDGWdk/KtZtBmMHpvJ1PwXRIUsSLlR70CMuPE6N5prjNJE5FcgXFNEmW0z7hS5YwfGFjw7h5RmxCOeZt+GE0TEBEGx69NyfMlShrE2lzjDPejg0tqqBzyigaF4jEZfg2C8gBsWxO6illDEvSTOpKILPwox/LnkGoR1iB47lcZqIssEbHtclJCCRR2WkyzE5Dyv3Y2TOU4jcu2OnpO8mf7rhEIrG9UCgcEcLsQjpOckaHMEYi/59QsqP51fwDDCv6HvL0yNFXwUSxdTmeaMfiC6FQ9FzYCr+x8/asIDHGpDrPBJ8lQRcNS+wt2IUkFr+HqUV3ftUOOq9OvUP0GFL4iwvesfbFgIcCoSHsbgg7msHJvTCsQEoIOZfNZn/jPWqlmqod4CgfIj1LpNionQ3O67CLxYn3oZ/CV3YU7JXhXO7PZyy+iNimi7tU7WAjEStyWHF1QjBhQXiAOOUQfo7mKKZStm1/9Qb+L8j3rXAgTJs1pOy6HlaTRm5yvQtYMzVr+AqQQS/RFUreOjjotDDFW+02R9AKDiIlqiI9TigU6tWv69JIilDmIo6usiAMoURM23VpSADV063NMsSZW7K+NCKAu8W6tF2GmHcnfPEViEQiu6GwTbvrKLkrFou1aq8mvgLWiuVWkCx560C0mM1a3u9NPXwFMizzB91TtMr7ILllPGZsKav95oixWCtu7X2UZw79cjgYHkbY+8eqD2P/AFyfJ1u/I+b/AAAAAElFTkSuQmCC',
    f"{BTN_CONFIGURE}.png": b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAQAAABKfvVzAAABM0lEQVR42rWUvUoDQRDHf5VygTslnp2C2JzWeQHtjFWIZ97BQp9B8Dl8ADsLMWqjRTobCQh+FEIuhVUgpkpxGYvbW3dyCZyCM83y/2B3ZpiFYuyTIAgJdUpFJheEXjmDOFkiKsqwMFt0SJcrdgA4U4ZjAGq0eeYgl0eMDd3lTcmFCQ/ckiIIY6LM0J4Szc82QMiktEHYgApfU2BCjI9Ps/DAEcsADQZKXrXNqNJ3mA/TFiB06ohV/1oWv8RzicgSvjIsWXxTT2LLEsEcw7YLh9xYoqkMscU7hD9zdot+ZcUp+t1hBjQAVu2c8+zTIiAgVnJBGOLB2q8GFwJclJZ3speuM0IQUq65L9z3wpM5pdTy4na549w07kTJT83SPvLJ0ezdWFQG7x9W9A+fQJ2eke8VyW8XRyaZm3NOsgAAAABJRU5ErkJggg==',
    f"{BTN_DOTTED_UNDERLINE}.png": b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAALiMAAC4jAXilP3YAAABnSURBVEhLY5R3t2NABw93HvoPZTIA5RmhTJwAn3omKE0zMGoBQTBqAUFAcwsIZjRSAVEZjZjcSyzAGUTUsgRrEJEKRssiisCoBQQBzS2gSj7AB2juA1DOA1GgnAjGID41xWjsAwYGANcTKLoAeDV3AAAAAElFTkSuQmCC',
    f"{BTN_SET_FONTS}.png": b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAQjSURBVEhLjVVbbBRVGP7O7L0t21a2tqWEQgSDFzCiVW6xYsGgRAkhVBP1xRCf9EEJkoCxWaMoaY1oSAyg8cGID0RNIMREC7IYMaBNTIxWoFub1mKV1g1lp7vb3Znjd2YPs0u32/I1nTn/Zf77+VdgFrR2SC8CE+d4XKFoI/GveimciLQs3Hy0XVianhaGfpeFDEzcy+cyTbqQkKsSPw/crsmymNWBkLKNT58mXQiJ2hzEak2WhetAlaL1HXO+Jh2QV0NT7Zq8EYKw7e3rd8WrNcfBuh39zZDSLX3+QMZDb6feFZAvS4lRMs8xxD6ynxICDY6ORlEPHEhgiN98Sb1l/J59EgwKr3zXuXC/ytNx0Pqmeb805EkBEVb0VNQGgeQkkLXzDoIsmNcQSGZofhqQO+w1/Ku79zUNelRppDd7mAnfpeUuAh5g853AnseAMM89lxlT2sT2Nj+2rvUjnQIuJ2zYU/ww6rCUuXBL0/4Thgyl19HnBi1zoYy/tAZ48REgMgeYX6sFRH2tgboaA89vDGDbSj/boQXFkKJ9bFH/fYawZQMVSlQ2LQUev4clmWHOlOzRFh9WNDOaKWDx/TY8dcbDmdBnzPBDzrV7YSIh4JmVMxu/DqWzZY3f6UsBMsvHG6dDn3xtRKPCDviu7SLjuCMjmliOajq5WdTfIlAVKiqCxOG6CrML0ajtxPjtzkbTlvYeSpx2zQlwSqZkXV0BBMmrYKSVxcaIgE8wgwLP46nZfTR6N+eOGTocwoOAe55u+JY3Awe2Aq8/HULD3NLa5UNTkDItrrkKzqFt79W5nPJDHDAnjHGOXzanTgUoweJGYF5dqfE070M6e92DED5Lfrxhxy+VijJ4D4I5+GgcbGsegwlgNKmJm8DQFRvJVCFvDsyTOaN637YO6TcQNJ+FtLeo3aLluJoBPv0RsHhzZ4PF2fvq7CQyRRnTELslXxgzBzYZlm1f4syW7PTuOPDFTzM7UcaP0fhvw6VK3GMTFnx/egZP7h1sPpNdwgSWa5kDixn3DAN9XA+rFvPKsPQqyfFMloYtJJjmgeM5fH/BKmqwC8k9916sa8ERg19JIbxvkXklLytA7ZgfhrhvxtP4x0xhJJlC/GIf+i/F8cfFYSfyaYwrXp+Rke8zJOmMRGx34IKEcVALR/j/ORv1mpTyL4fHP4vecraNycwkchwxypRIyeIsMXVxjJwxxRPC6Dr1wW3OXncb6/z2VpqR2KtVI5qFBzpGw0F/8JuPnpt4MKRXQe+vvzvvMdOHQ2cbT9sVlU/EovXuzK3f2Tuvu3Pp3yp6RbtDHYuKXLFxhfPRyDj1jjgplILzIQ4WG1fo7rxDLXVXv/TWTAFVT3FtqOV1A4Je+z+vzzivybKY1cGtS6p6OUE9mnQR9MszawMLBjRZBsD/VTKT1KVjgdAAAAAASUVORK5CYII=',
    f"{BTN_INSERT_ACCENT}.png": b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAABhmlDQ1BJQ0MgcHJvZmlsZQAAKM+VkT1Iw1AUhU9TRSkVBzuIOmSoThakigguEsUiWChthVYdTF76B00akhQXR8G14ODPYtXBxVlXB1dBEPwBcXRyUnSREu9LCi1CBS883sd57xzuuw8Q6mWmWV0TgKbbZjImiZnsqtjzigCG4UMUszKzjHhqMY2O9XVPN6nuIjwL/6s+NWcxwCcSzzHDtIk3iKc3bYPzPnGIFWWV+Jx43KQGiR+5rnj8xrngssAzQ2Y6OU8cIhYLbay0MSuaGvEUcVjVdMoXMh6rnLc4a+Uqa/bJXxjM6SsprtMaQQxLiCMBEQqqKKEMGxHadVIsJOlc6uAfcv0JcinkKoGRYwEVaJBdP/gf/J6tlZ+MeklBCeh+cZyPUaBnF2jUHOf72HEaJ4D/GbjSW/5KHZj5JL3W0sJHQP82cHHd0pQ94HIHGHwyZFN2JT8tIZ8H3s/om7LAwC0QWPPm1jzH6QOQplkt3wAHh8BYgbLXO7y7t31uf95x5wfpB/5fct+mrTaGAAAACXBIWXMAAA7BAAAOwQG4kWvtAAAAB3RJTUUH5gobATQys15SQAAAABJ0RVh0U29mdHdhcmUAR3JlZW5zaG90XlUIBQAAAM5JREFUSEtjGAVUB/+PF/+XB1IgZtCq/yCaeuD/72v/q9UghjNoVf8/95PKFtzrMwcbzmzS8v/ab2q7/vWc/45Ait9zzv971DYcBO716f8XDV36/zktDKcL+P/72P9ieWDkikb9X/uZBr74f736vzqQYmBg/h+1iQoWXGvT/8/MIPo/at0PsGHYfPBzXdR/UaCUaOZe0iz8/x8pvYeuxal5aywzRI1aNVAHib5C9wE2QLYPRgFRgKZxMCCpiKr5ABugek5GBzQviwYpYGAAACrQwIYqJkYSAAAAAElFTkSuQmCC',
    f"{BTN_SWITCH_TOOLBAR}.png": b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAACxMAAAsTAQCanBgAAANdSURBVEhL1VRJT1NRFOZ2ptCWltLSkoBlKhbC1IKUkBChERYVF4bEsIGNjS7cuHDDAhMT/4ArdcGWUBeiC4c4IDGlMdDEaIpYNMEYgTbKEEpoX5v6ndcnKU0NqBjjSV7eu+fe+31n+M7L++9NLLx583g8UovFIg8Gg0nBdXRG4BqN5jqeqYGBARVcLL1zROZ2u5UAvy8SieKFhYXP7Xa7Hu5cJL9NzChygD9jjMULCgpmm5qaylKp1B4gslQODQ1pKVssRXh+mYxR5AD3IZNdvOdbW1tNY2NjIvg1IH8sFos/yeXyVzU1NaP19fVV3d3dEuHuoY1R5Gq12keZKJXK2cHBQU1HR4cOhAH4SAApBMDJZLJVo9F4Ffv7xJJpOTcAro5Go2fi8fixRCJRtry83KnVau+MjIzcNJvN4yCZ2dnZkWH/+Pb2tmtlZcVWXV39JBwO7woQPzXW0NBgRNRvEWEMpZjNz89/CUCOykaZUbnoHEXtdDo7JRJJSOjZtM1m06Vhchvr7++X63S6e3QBwNM9PT3GkpKSW1gnBJB5lGqv8UTW1dVVKZVKFykgvV7vJQweLdvoMOp5BUBJXPjY3t5ugZsBdAnrb6haEHscsvNRTzJJkLUDzf+KZbK0tPSikOU+Yy6XSyM0MY5pHsUhXh3whUAQrqurswPcTyQk5cw5mZycFJtMpnGaoaKioqc5lUWs5eXl54kA6viMejZTnQ0Gww0CxRA+tFqtJwG+SGsQ+1paWsx0r7GxsRa9iNBdYJzNnJ19RlEXFxffpkjQ4PdoajPVHBm8Ix/KEMWblJIkMMqY5gS9KkPPZpDFtWzJZjMxAGoXFhbubm1tOQH8BfK7BLLXkUjk8sbGRh9IOPRjYn193Q0pO1C2ud7e3lPIJkY/Sa/Xe+CPkkF+BvovUZR4YsjKC/2fg2JOtLW1OaEWj0qlmsNZUlfigH9XTmPDw8OKioqKC+jHEsrCAYgvCx7+G76YQqEIofbUEyoXPyd0Nw2RtoMYGdSjQ6n61tbWTm9ublbCl8KsLGI+plC6FyiRyu/3P+A4rgp9eAMhuAOBwCqd4xEOY6QUUgY1kL5/rIVt5nA4rMj0A/oTA/lEdqP/2IgM/anFDDyiYaUAhK0jNUYD9rfA/5Xl5X0HEO4mtVMUk+QAAAAASUVORK5CYII=',
    f"{BTN_CHECK_PAIRS}.png": b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAACxMAAAsTAQCanBgAAAF1SURBVEhL3dZNKwVRHMfxQXncKAskDztkY63IhpINC0/vwEJJ8Q68ARZKKYkVdrKTusVaFjay0n0BHhZE4vubmXub+7/nzNyUyK8+d87858zMueeemW7w06mKt74soDdqluQCZ5hHnwomz9jBY7jnyTg+PXThEVOzNhFU68OT9njrikbYGjW9adNH2hQ1oyNqluUeOrcz3HNH05NPu8EAZqJmWQ6hc33HlRscRU13ZuGaW9GF50zN0iBSf4OsZK3AMH/6BhWd+7+nqC7e2pwjh4Zw75vREn1Actl9YB010KviCcnjVrhMbeqxBdtZT+UYdHw7rmXZRUm6cQXb8R3D6MF1XKvEGoppxC1cHTXiJtwlalle0YViFuHqKENYMrUsKyjJHlwdRW/VA1PzecMyiiks05d460ot9JWzkscoNsI9kwm4RiRTmDQ16wQtSI1reWrkhXe+67imZBUVPdXKNI5xCa2efiSjPwGn0HLexyB+M0HwBbTztQD+GrWZAAAAAElFTkSuQmCC',
}
