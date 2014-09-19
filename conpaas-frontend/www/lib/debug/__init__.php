<?php
require_module('director');
$js_debug_level = Director::getJsDebugLevel();
$ajax_debug_level = Director::getAjaxDebugLevel();
$php_debug_level = Director::getPhpDebugLevel();
$python_debug_level = Director::getPythonDebugLevel();
?>
<script src="/js/debug.js"></script>
<script>
<?php echo "JS_DEBUG_LEVEL=$js_debug_level;\n" ?>
<?php echo "AJAX_DEBUG_LEVEL=$ajax_debug_level;\n" ?>
<?php echo "PHP_DEBUG_LEVEL=$php_debug_level;\n" ?>
<?php echo "PYTHON_DEBUG_LEVEL=$python_debug_level;\n" ?>
</script>
