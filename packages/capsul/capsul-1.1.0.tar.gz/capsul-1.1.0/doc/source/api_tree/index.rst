:orphan:

######
API
######

The exact API of all functions and classes, as given by the docstrings.

**User guide:** See the :ref:`capsul_guide` section for further details.

.. _capsul_ref:

:mod:`capsul.pipeline`: Pipeline
=================================

.. currentmodule:: capsul.pipeline

Pipeline Definition
-------------------

.. autosummary::
    :toctree: generated/capsul-pipeline/
    :template: class.rst

    pipeline.Pipeline

Node Types
----------

.. autosummary::
    :toctree: generated/capsul-pipeline/
    :template: class.rst

    pipeline_nodes.Node
    pipeline_nodes.ProcessNode
    pipeline_nodes.PipelineNode
    pipeline_nodes.Switch

Plug
-----

.. autosummary::
    :toctree: generated/capsul-pipeline/
    :template: class.rst

    pipeline.Plug

Workflow conversion
-------------------

.. autosummary::
    :toctree: generated/capsul-pipeline/
    :template: function.rst

    pipeline_workflow.workflow_from_pipeline
    pipeline_workflow.local_workflow_run

    pipeline_tools.pipeline_node_colors
    pipeline_tools.pipeline_link_color
    pipeline_tools.dot_graph_from_pipeline
    pipeline_tools.save_dot_graph
    pipeline_tools.save_dot_image
    pipeline_tools.nodes_with_existing_outputs
    pipeline_tools.nodes_with_missing_inputs
    pipeline_tools.disable_runtime_steps_with_existing_outputs
    pipeline_tools.where_is_plug_value_from
    

:mod:`capsul.process`: Process
===============================

.. currentmodule:: capsul.process

Classes
-------

.. autosummary::
    :toctree: generated/capsul-process/
    :template: class_process.rst

    process.Process
    process.NipypeProcess
    process.FileCopyProcess

    :template: class.rst

    process.ProcessResult
    process_with_fom.ProcessWithFom

Functions
---------

.. autosummary::
    :toctree: generated/capsul-process/
    :template: function.rst

    loader.get_process_instance


:mod:`capsul.study_config`: Study Configuration
===============================================

.. currentmodule:: capsul.study_config

Study Configuration
-------------------

.. autosummary::
    :toctree: generated/capsul-studyconfig/
    :template: class.rst

    study_config.StudyConfig
    memory.Memory

Configuration Modules
---------------------

.. currentmodule:: capsul.study_config.config_modules

.. autosummary::
    :toctree: generated/capsul-studyconfig/
    :template: class.rst

    matlab_config.MatlabConfig
    spm_config.SPMConfig
    fsl_config.FSLConfig
    freesurfer_config.FreeSurferConfig
    nipype_config.NipypeConfig
    brainvisa_config.BrainVISAConfig
    fom_config.FomConfig

