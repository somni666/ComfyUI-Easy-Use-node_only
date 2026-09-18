# Background behavior audit

This fork intentionally leaves ComfyUI in charge of model lifetime, loading,
offloading, and memory reclamation.

## Removed behavior

### Persistent model caches

The pack maintained two process-global caches in addition to ComfyUI's cache:

* `py.easyCache` retained checkpoints, UNets, CLIPs, VAEs, LoRAs, ControlNets,
  T5, and ChatGLM objects.
* `py.libs.cache.cache` retained adapter, InsightFace, InstantID, PuLID, IC-Light,
  BrushNet, PowerPaint, and other objects.

Both caches held strong references, so ComfyUI could unload an object from its
own cache without Python being able to reclaim it. Both APIs are now no-retention
compatibility facades: existing nodes still load resources, but the resources are
owned by the workflow outputs and ComfyUI rather than this extension.

### Process-wide monkey patches

The bundled BrushNet/PowerPaint implementation replaces
`comfy.samplers.sample` and ComfyUI's global `apply_control` function and does not
restore either replacement. The LayerDiffuse implementation similarly replaces
the global LoRA/ModelPatcher weight-calculation function and does not restore it.
Those nodes have therefore been unregistered. The combined inpaint node no longer
offers its BrushNet or PowerPaint modes.

LayerDiffuse also installed an import-time wrapper around
`BasicTransformerBlock.forward`, meaning it affected every workflow merely by
loading this extension. That wrapper has been removed; importing the disabled
LayerDiffuse implementation no longer mutates a ComfyUI class.

Fooocus inpaint remains available. Its temporary weight-calculation override is
scoped to a context manager around sampling and is restored afterward. Kolors'
loader overrides are likewise scoped to its loader operation and restored.

## Remaining integration hooks

The extension still registers HTTP routes and a prompt handler. The prompt
handler implements the explicitly selected `easy globalSeed` workflow feature;
it does not modify model management. Startup also registers model-directory
categories with `folder_paths`. These integrations add extension functionality
but do not replace ComfyUI model loading, caching, or unloading behavior.

The HTTP API includes user-invoked administration actions. In particular,
`/easyuse/cleangpu` asks ComfyUI to unload all models and empty its cache, while
`/easyuse/reboot` restarts the process. Neither action runs automatically or as a
background task. The configured web extension also registers global ComfyUI UI
enhancements whenever the browser loads; these affect the editor rather than the
backend model lifecycle.

Model patchers used by IP-Adapter, IC-Light, Fooocus, dynamic CFG, and similar
nodes are attached to cloned model objects during those nodes' execution. They
are not process-wide replacements of ComfyUI functions.
