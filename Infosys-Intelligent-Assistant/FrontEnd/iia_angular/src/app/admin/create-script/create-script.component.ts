/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, ViewEncapsulation, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { NgbModal, NgbActiveModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
import { ArgsComponent } from '../../ticket/arg-popup/arg-popup.component'
const defaults = {
  'python': `# Add other fuctions below but do not change the main function name
def main(param1,param2,...):
  # Write your code here`
};
@Component({
  selector: 'app-create-script',
  templateUrl: './create-script.component.html',
  styleUrls: ['./create-script.component.css'],
  encapsulation: ViewEncapsulation.None
})
export class CreateScriptComponent implements OnInit {
  @Input() dataToTakeAsInput: any;
  readOnly = false;
  mode = 'python';
  options: any = {
    lineNumbers: true,
    theme: 'dracula',
    mode: this.mode,
    extraKeys: { 'Ctrl-Space': 'autocomplete' }
  }
  default: any = {};
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
  argsArray: any = [];
  argDataTypes: Array<string> = ['str', 'int', 'float', 'list', 'tuple', 'range', 'dict', 'set', 'bool', 'bytes', 'bytearray']
  @Output() emitData = new EventEmitter();
  ArgsMessage: string = "Enter valid python datatypes. Ex: str, int, 'list', 'dict', 'bool'"
  flag: boolean = false;
  constructor(private httpClient: HttpClient, private modalService: NgbModal, public activeModal: NgbActiveModal) {
  }
  ngOnInit() {
    if (this.dataToTakeAsInput['Content']) {
      this.default[this.mode] = this.dataToTakeAsInput['Content']
      this.scriptName = this.dataToTakeAsInput['Name']
      this.argTypes = this.dataToTakeAsInput['Args']
      this.scriptNameStatus = false;
    } else {
      this.default = defaults
      this.scriptNameStatus = true;
    }
  }
  getScriptNames() {
    this.httpClient.get('/api/getScriptsFromPath').subscribe(data => {
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
    this.default[this.mode] = `# Add other fuctions below but do not change the main function name
def main(param1,param2,...):
  # Write your code here`;
  }
  provideArgs() {
    this.flag = false;
    let formdata = new FormData()
    if (typeof this.argTypes == 'string') {
      this.argTypes = this.argTypes.trim().split(',')
    }
    // Checking for empty datatypes
    if (this.argTypes.length == 0) {
      this.type = 'warning';
      this.message = 'Give respective datatypes';
      this.scriptStatus = true;
    } else if (this.argTypes.length == 1) {
      if (this.argTypes[0] === "") {
        this.type = 'warning';
        this.message = 'Give respective datatypes';
        this.scriptStatus = true;
      }
    }
    //Checking for valid datatypes
    for (let i = 0; i < this.argTypes.length; i++) {
      if (this.argDataTypes.includes(this.argTypes[i])) {
        this.flag = false;
      } else {
        this.flag = true
        break
      }
    }
    if (this.flag == true) {
      this.type = 'warning';
      this.message = 'Give correct datatypes';
      this.scriptStatus = true;
    } else {
      formdata.append('Script', this.default[this.mode])
      this.httpClient.post('/api/getArgumentsFromFile', formdata).subscribe(data => {
        this.argsArray = data;
        //Check for number mismatch of arguments
        if (this.argTypes.length == this.argsArray.length) {
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
          this.message = 'Incorrect number of datatypes';
          this.scriptStatus = true;
        }
      });
    }
  }
  saveScript() {
    if (this.argTypes.length > 0) {
      if (typeof this.argTypes == 'string') {
        this.argTypes = this.argTypes.trim().split(',')
      }
      this.getScriptNames()
      if (!(this.scriptName in this.scriptsList) && this.scriptName.length != 0) {
        let formdata = new FormData()
        formdata.append('Script', this.default[this.mode])
        formdata.append('Name', this.scriptName)
        formdata.append('Type', this.dataToTakeAsInput['Type'])
        formdata.append('Arguments', this.argTypes)
        this.httpClient.post('/api/SaveCode', formdata, { responseType: 'text' }).subscribe(data => {
          alert(data)
          if (data == 'Success') {
            if (this.compileResponse == false) {
              this.message1 = "Warning : Make sure the code is correct since it is not compiled"
              this.noCompile = true;
            }
            this.message = "Please Refresh to map diagnostic scripts"
            this.saveSuccess = true;
            this.emitData.next(this.argTypes)
          }
        })
      }
      else {
        alert("Either Script Name exists or Script Name is empty")
      }
    } else {
      this.type = 'warning';
      this.message = 'Give respective datatypes';
      this.scriptStatus = true;
    }
  }
  closeAlert() {
    this.scriptStatus = false;
  }
}
