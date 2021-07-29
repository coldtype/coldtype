
Cheatsheet
==========

* **PreviewPrevMany** (``"prev_prev_many"``)

  Go n-frames backward (cycling)

  * ``shift j``
  * ``shift <left>``


* **PreviewPrev** (``"prev_prev"``)

  Go to the previous frame

  * ``j``
  * ``<left>``


* **PreviewNextMany** (``"prev_next_many"``)

  Go n-frames forward (cycling)

  * ``shift l``
  * ``shift <right>``


* **PreviewNext** (``"prev_next"``)

  Go to the next frame

  * ``l``
  * ``<right>``


* **ClearLastRender** (``"clear_last_render"``)

  When compositing, delete the existing framebuffer

  * ``<backslash>``


* **ClearRenderedFrames** (``"clear_rendered_frames"``)

  Delete all the rendered frames on disk for this animation

  * ``shift <backslash>``


* **PlayRendered** (``"play_rendered"``)

  Play the rendered-to-disk version of this animation

  * ``shift <space>``


* **PlayPreview** (``"play_preview"``)

  Play the current animation as fast as possible, evaluating the code live

  * ``<space>``


* **RestartApp** (``"restart_app"``)

  Restart the app (a shortcut for when you've modified code that isn't reloaded automatically on save)

  * ``cmd r``


* **Quit** (``"quit"``)

  Quit the app and stop the renderer completely (alias of hitting the window X or hitting Ctrl-C in the terminal)

  * ``q``


* **Release** (``"release"``)

  Trigger the custom ``release`` function (if there's one defined in your code)

  * ``r``


* **Build** (``"build"``)

  Trigger the custom ``build`` function (if there’s one defined in your code)

  * ``b``


* **RenderAll** (``"render_all"``)

  Render all the frames in this animation to disk

  * ``a``


* **RenderOne** (``"render_one"``)

  Render just the current frame to disk

  * ``cmd a``


* **RenderWorkarea** (``"render_workarea"``)

  Render the workarea to disk (if a workarea is defined)

  * ``w``


* **ToggleMultiplex** (``"toggle_multiplex"``)

  Toggle multiplexing (multicore rendering) on and off

  * ``m``


* **OverlayInfo** (``"overlay_info"``)

  Turn on the “info” overlay

  * ``/``


* **OverlayRendered** (``"overlay_rendered"``)

  Turn on the “rendered” overlay (only used in the blender workflow for previewing a blender-rendered frame)

  * ``'``


* **PreviewScaleUp** (``"preview_scale_up"``)

  Enlarge the viewer

  * ``=``


* **PreviewScaleDown** (``"preview_scale_down"``)

  Shrink the viewer

  * ``-``


* **PreviewScaleMin** (``"preview_scale_min"``)

  Make the viewer as small as possible

  * ``cmd -``


* **PreviewScaleMax** (``"preview_scale_max"``)

  Make the viewer as large as possible

  * ``cmd =``


* **PreviewScaleDefault** (``"preview_scale_default"``)

  Make the viewer the standard size (100%)

  * ``cmd 0``


* **WindowOpacityDown** (``"window_opacity_down"``)

  Make the viewer more transparent

  * ``cmd <down>``


* **WindowOpacityUp** (``"window_opacity_up"``)

  Make the viewer less transparent

  * ``cmd <up>``


* **WindowOpacityMin** (``"window_opacity_min"``)

  Make the viewer as transparent as possible

  * ``cmd shift <down>``


* **WindowOpacityMax** (``"window_opacity_max"``)

  Make the viewer fully opaque

  * ``cmd shift <up>``


* **OpenInEditor** (``"open_in_editor"``)

  Open the currently-rendered file in your code editor

  * ``o``


* **ViewerSoloNone** (``"viewer_solo_none"``)

  View all defined renderables and animations

  * ``np0``
  * ``0``


* **ViewerSoloNext** (``"('viewer_solo_next',)"``)

  Solo the “next” animation/renderable in the file

  * ``cmd <right>``


* **ViewerSoloPrev** (``"('viewer_solo_prev',)"``)

  Solo the “previous” animation/renderable in the file

  * ``cmd <left>``


* **ViewerSolo1** (``"viewer_solo_1"``)

  Solo the first animation/renderable in the file

  * ``np1``
  * ``1``


* **ViewerSolo2** (``"viewer_solo_2"``)

  Solo the second animation/renderable in the file

  * ``np2``
  * ``2``


* **ViewerSolo3** (``"viewer_solo_3"``)

  Solo the third animation/renderable in the file

  * ``np3``
  * ``3``


* **CopySVGToClipboard** (``"copy_svg_to_clipboard"``)

  Copy the current vector to the clipboard as SVG (can be pasted into Illustrator)

  * ``cmd c``


* **LoadNextInDirectory** (``"load_next_in_directory"``)

  If you have a directory of coldtype .py files, this will load the next one in the directory (alphabetically), so you can skip stopping and restarting the command-line process with different arguments

  * ``cmd alt <right>``


* **LoadPrevInDirectory** (``"load_prev_in_directory"``)

  If you have a directory of coldtype .py files, this will load the previous one in the directory (alphabetically), so you can skip stopping and restarting the command-line process with different arguments

  * ``cmd alt <left>``


