/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, ViewEncapsulation, OnInit, Input, Output, EventEmitter, ViewChild } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { NgbModal, NgbActiveModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
import { ArgsComponent } from '../../ticket/arg-popup/arg-popup.component'
const defaults = {
  'json': `{
  "BotName" : "",
  "InArguments" : {
      "" : {
          "type" : ""
      }
  },
  "DevicePoolName" : "",
  "ControlRoomUrl" : "Enter VM name here" 
}`
};
const defaultsUiPath = {
  'json': `{
   "TenantName" : "",
   "ProcessName" : "",
   "InArguments" : {
       "" : {
           "type" : ""
       }
   },
   "OrchestratorUrl" : "Enter VM name here"
 }`
};
const defaultsBluePrism = {
  'json': `{
    "XmlName" : "",
    "ServiceName" : "",
    "InArguments" : {
        "" : {
            "type" : ""
        },
        "" : {
            "type" : ""
        }
    }
  }`
};
@Component({
  selector: 'app-create-rpa',
  templateUrl: './create-rpa.component.html',
  styleUrls: ['./create-rpa.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class CreateRPAComponent implements OnInit {
  @Input() dataToTakeAsInput: any;
  readOnly = false;
  mode = 'json';
  options: any = {
    lineNumbers: true,
    theme: 'dracula',
    mode: this.mode,
    extraKeys: { 'Ctrl-Space': 'autocomplete' }
  }
  default: any = {};
  defaultUiPath: any = {};
  type: string;
  message: string;
  saveSuccess: boolean;
  scriptStatus: boolean;
  scriptName: string = '';
  scriptsList: any = []
  scriptNameStatus: boolean;
  noCompile: boolean = false;
  compileResponse: boolean = false;
  message1: string;
  argList: any = {}
  argTypes: any = []
  @Output() emitData = new EventEmitter();
  ChoosenRPA: any = 'AutomationAnywhere';
  configType: any;
  configTitle: string;
  constructor(private httpClient: HttpClient, private modalService: NgbModal, public activeModal: NgbActiveModal) {
  }
  ngOnInit() {
    if (this.dataToTakeAsInput['Content']) {
      this.default[this.mode] = this.dataToTakeAsInput['Content']
      this.scriptName = this.dataToTakeAsInput['Name']
      this.ChoosenRPA = this.dataToTakeAsInput['RpaType']
      this.configType = this.dataToTakeAsInput['Type']
      if (this.configType == 'RPA') {
        this.configTitle = 'Create Config'
      } else {
        this.configTitle = 'Create Diagnostic Config'
      }
      this.scriptNameStatus = false;
    } else {
      this.configType = this.dataToTakeAsInput['Type']
      if (this.configType == 'RPA') {
        this.configTitle = 'Create Config'
      } else {
        this.configTitle = 'Create Diagnostic Config'
      }
      this.default = defaults
      this.scriptNameStatus = true;
    }
  }
  getScriptNames() {
    this.httpClient.get('/api/getRPAFromPath').subscribe(data => {
      this.scriptsList = data;
    })
  }
  changeMode() {
    this.options = {
      ...this.options,
      mode: this.mode,
    };
  }
  handleChange($event) {
    this.compileResponse = false;
  }
  clear() {
    if (this.ChoosenRPA == "AutomationAnywhere") {
      this.default[this.mode] = `{
  "BotName" : "",
  "InArguments" : {
      "" : {
          "type" : ""
      }
  },
  "DevicePoolName" : "",
  "ControlRoomUrl" : "Enter VM name here"
}`;
    } else if (this.ChoosenRPA == "UIPath") {
      this.default[this.mode] = `{
  "TenantName" : "",
  "ProcessName" : "",
  "InArguments" : {
      "" : {
          "type" : ""
      }
  },
  "OrchestratorUrl" : "Enter VM name here"
}`;
    } else if (this.ChoosenRPA == "BluePrism") {
      this.default[this.mode] = `{
  "XmlName" : "",
  "ServiceName" : "",
  "InArguments" : {
      "" : {
          "type" : ""
      },
      "" : {
          "type" : ""
      }
  }
}`;
    }
  }
  provideArgs() {
    if (this.argTypes.length > 0) {
      if (typeof this.argTypes == 'string') {
        this.argTypes = this.argTypes.trim().split(',')
      }
      if (this.default[this.mode].length != 0) {
        const modalRef = this.modalService.open(ArgsComponent, { size: 'lg', windowClass: 'app-modal-window', backdrop: false });
        modalRef.componentInstance.emitData.subscribe(($e) => {
          this.compileResponse = $e
        })
        let dataPassToChild: any = {};
        dataPassToChild['DataTypes'] = this.argTypes
        dataPassToChild['Script'] = this.default[this.mode];
        (<ArgsComponent>modalRef.componentInstance).dataToTakeAsInput = dataPassToChild;
        modalRef.result.then((result) => {
          console.log(result);
        }).catch((result) => {
          console.log(result);
        });
      }
    } else {
      this.type = 'warning';
      this.message = 'Give respective datatypes';
      this.scriptStatus = true;
    }
  }
  relatedConfig() {
    if (this.ChoosenRPA == "AutomationAnywhere") {
      if (this.dataToTakeAsInput['Content']) {
        this.default[this.mode] = this.dataToTakeAsInput['Content']
        this.scriptName = this.dataToTakeAsInput['Name']
        this.ChoosenRPA = this.dataToTakeAsInput['RpaType']
        this.configType = this.dataToTakeAsInput['Type']
        if (this.configType == 'RPA') {
          this.configTitle = 'Create Config'
        } else {
          this.configTitle = 'Create Diagnostic Config'
        }
        this.scriptNameStatus = false;
      } else {
        this.configType = this.dataToTakeAsInput['Type']
        if (this.configType == 'RPA') {
          this.configTitle = 'Create Config'
        } else {
          this.configTitle = 'Create Diagnostic Config'
        }
        this.default = defaults
        this.scriptNameStatus = true;
      }
    } else if (this.ChoosenRPA == "UIPath") {
      if (this.dataToTakeAsInput['Content']) {
        this.default[this.mode] = this.dataToTakeAsInput['Content']
        this.scriptName = this.dataToTakeAsInput['Name']
        this.ChoosenRPA = this.dataToTakeAsInput['RpaType']
        this.configType = this.dataToTakeAsInput['Type']
        if (this.configType == 'RPA') {
          this.configTitle = 'Create Config'
        } else {
          this.configTitle = 'Create Diagnostic Config'
        }
        this.scriptNameStatus = false;
      } else {
        this.configType = this.dataToTakeAsInput['Type']
        if (this.configType == 'RPA') {
          this.configTitle = 'Create Config'
        } else {
          this.configTitle = 'Create Diagnostic Config'
        }
        this.default = defaultsUiPath
        this.scriptNameStatus = true;
      }
    } else if (this.ChoosenRPA == "BluePrism") {
      if (this.dataToTakeAsInput['Content']) {
        this.default[this.mode] = this.dataToTakeAsInput['Content']
        this.scriptName = this.dataToTakeAsInput['Name']
        this.ChoosenRPA = this.dataToTakeAsInput['RpaType']
        this.configType = this.dataToTakeAsInput['Type']
        if (this.configType == 'RPA') {
          this.configTitle = 'Create Config'
        } else {
          this.configTitle = 'Create Diagnostic Config'
        }
        this.scriptNameStatus = false;
      } else {
        this.configType = this.dataToTakeAsInput['Type']
        if (this.configType == 'RPA') {
          this.configTitle = 'Create Config'
        } else {
          this.configTitle = 'Create Diagnostic Config'
        }
        this.default = defaultsBluePrism
        this.scriptNameStatus = true;
      }
    }
  }
  saveScript() {
    this.getScriptNames()
    if (!(this.scriptName in this.scriptsList) && this.scriptName.length != 0) {
      if (this.ChoosenRPA != undefined) {
        let formdata = new FormData()
        formdata.append('Script', this.default[this.mode])
        formdata.append('Name', this.scriptName)
        formdata.append('RpaType', this.ChoosenRPA)
        formdata.append('Type', this.dataToTakeAsInput['Type'])
        this.httpClient.post('/api/SaveRPA1', formdata, { responseType: 'text' }).subscribe(data => {
          if (data == 'Success') {
            this.saveSuccess = true;
            this.message1 = "Note : Please map keywords for the Bot in Micro-Bot Mapping"
          }
        })
      } else {
        alert('Select Respectice RPA Tool')
      }
    } else {
      alert('Provide Bot Name');
      this.scriptStatus = true;
    }
  }
}
