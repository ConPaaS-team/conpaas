<?php
/*
 * Copyright (c) 2010-2014, Contrail consortium.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms,
 * with or without modification, are permitted provided
 * that the following conditions are met:
 *
 *  1. Redistributions of source code must retain the
 *     above copyright notice, this list of conditions
 *     and the following disclaimer.
 *  2. Redistributions in binary form must reproduce
 *     the above copyright notice, this list of
 *     conditions and the following disclaimer in the
 *     documentation and/or other materials provided
 *     with the distribution.
 *  3. Neither the name of the Contrail consortium nor the
 *     names of its contributors may be used to endorse
 *     or promote products derived from this software
 *     without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
 * CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
 * INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 * BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

require_module('ui/instance');

class GenericInstance extends Instance {

    private $scriptStatus = null;

    public function __construct($info, $sid, $scriptStatus) {
        parent::__construct($info);
        $this->sid = $sid;
        $this->scriptStatus = $scriptStatus;
    }

    protected function renderCapabs() {
        $html = '';
        if ($this->info['is_master']) {
            $html .= '<div class="tag blue">&nbsp;master&nbsp;</div>';
        } else {
            $html .= '<div class="tag orange">node</div>';
        }
        return $html;
    }

    public function renderScriptStatus($script) {
        $text = $this->scriptStatus[$script];
        $toolTipText = '';
        $img = 'ledgray.png';
        $class = '';
        if (strpos($text, 'STOPPED') !== false) {
            $toolTipText = substr($text, 9, strlen($text) - 10);
            $text = 'STOPPED';
            $img = 'ledred.png';
        } elseif ($text == 'RUNNING') {
            $img = 'ledgreen.png';
            $class = ' class="running"';
        } elseif ($text == 'NEVER STARTED') {
            $img = 'ledlightblue.png';
        }
        return
            '<tr>'
                .'<td><b>'.$script.'</b>&nbsp;&nbsp;&nbsp;</td>'
                .'<td title="'.$toolTipText.'">'
                    .'<img'.$class.' width="10" height="10" src="images/'.$img.'">'
                    .'&nbsp;'.$text
                .'</td>'
            .'</tr>';
    }

    public function renderScriptStatusTable() {
        if ($this->scriptStatus == null) {
            return '';
        }
        $html =
            '<div class="generic-script-status">'
                .'<table cellspacing="0" cellpadding="0">'
                    .$this->renderScriptStatus('init.sh')
                    .$this->renderScriptStatus('notify.sh')
                    .$this->renderScriptStatus('run.sh')
                    .$this->renderScriptStatus('interrupt.sh')
                    .$this->renderScriptStatus('cleanup.sh')
                .'</table>'
            .'</div>';
        return $html;
    }

    public function renderAgentLogs() {
        $linkAgentLogs = LinkUI('agent log',
            'viewlog.php?sid='.$this->sid
            .'&agentId='.$this->info['id']
        )->setExternal(true);
        $linkAgentOut = LinkUI('agent output',
            'viewlog.php?sid='.$this->sid
            .'&agentId='.$this->info['id']
            .'&filename=agent.out'
        )->setExternal(true);
        $linkAgentErr = LinkUI('agent error',
            'viewlog.php?sid='.$this->sid
            .'&agentId='.$this->info['id']
            .'&filename=agent.err'
        )->setExternal(true);
        $html =
            '<div class="generic-agent-logs">'
                .$linkAgentLogs
                .$linkAgentOut
                .$linkAgentErr
            .'</div>';
        return $html;
    }

    public function render() {
        return
        '<div class="instance dualbox">'
            .'<div class="left">'
                .'<i class="title">Instance '.$this->info['id'].'</i>'
                .$this->renderCapabs()
                .'<div class="brief">running</div>'
            .'</div>'
            .'<div class="left">'
                .$this->renderScriptStatusTable()
            .'</div>'
            .'<div class="left">'
                .$this->renderAgentLogs()
            .'</div>'
            .'<div class="right">'
                .'<i class="address">'.$this->info['ip'].'</i>'
            .'</div>'
            .'<div class="clear"></div>'
        .'</div>';
    }

    public function renderInCluster() {
        return
        '<div class="instance dualbox">'
            .'<div class="left">'
                .'<i class="title">Instance '.$this->info['id'].'</i>'
                .'<span class="timestamp">running</span>'
            .'</div>'
            .'<div class="left">'
                .$this->renderScriptStatusTable()
            .'</div>'
            .'<div class="left">'
                .$this->renderAgentLogs()
            .'</div>'
            .'<div class="right">'
                .'<i class="address">'.$this->info['ip'].'</i>'
            .'</div>'
            .'<div class="clear"></div>'
        .'</div>';
    }
}

?>
