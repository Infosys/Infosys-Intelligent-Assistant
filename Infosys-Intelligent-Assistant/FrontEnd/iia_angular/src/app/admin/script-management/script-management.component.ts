/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { FormBuilder, FormControl, FormArray, FormGroup, Validators } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { ResponseType } from '@angular/http';
import { text, template } from '@angular/core/src/render3';
import { COMMA, ENTER } from '@angular/cdk/keycodes';
import { Component, ElementRef, ViewChild, OnInit, Injectable } from '@angular/core';
import { MatAutocompleteSelectedEvent, MatChipInputEvent, MatAutocomplete } from '@angular/material';
import { Observable } from 'rxjs';
import { map, startWith } from 'rxjs/operators';
import { coerceNumberProperty } from '@angular/cdk/coercion'
import { MatTableDataSource, MatPaginator, MatSort, MatPaginatorModule, MatTableModule } from '@angular/material';
import { CreateScriptComponent } from '../create-script/create-script.component'
import { NgbModal, NgbActiveModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
import { forEach } from '@angular/router/src/utils/collection';
export interface UserData {
  Selected: any;
  scriptName: string;
  scriptEdit: string;
  diagnostic_script: string;
  diagnosticEdit: string;
}
@Component({
  selector: 'app-script-management',
  templateUrl: './script-management.component.html',
  styleUrls: ['./script-management.component.css'],
})
export class ScriptManagementComponent implements OnInit {
  displayedColumns: string[] = ['Selected', 'scriptName', 'scriptEdit', 'diagnostic_script', 'diagnosticEdit'];
  dataSource: MatTableDataSource<UserData>;
  message: string;
  saveSuccess: boolean = false;
  @ViewChild(MatPaginator) paginator: MatPaginator;
  @ViewChild(MatSort) sort: MatSort;
  selectedAll: any;
  updation: boolean;
  addition: boolean = true;
  removal: boolean;
  keywordCtrl = new FormControl();
  filteredKeywords: Observable<string[]>;
  deploymentStatus: boolean;
  scriptName: string = "";
  args: boolean;
  toBeEdittedScript: string;
  invert = false;
  showTicks = false;
  thumbLabel = false;
  value: any;
  vertical = false;
  argumentCtrl = new FormControl();
  filteredArguments: Observable<string[]>;
  // disabledList: any[] = []
  public scriptsInfo: UserData[] = [];
  scripts = [];
  operation: any;
  tempList: any
  closeResult: any;
  scriptsList: any = []
  diagnosticScriptsList: any = []
  accessStatus: boolean;
  accessList: any[] = [];
  scriptDropdown = []
  argDict: any = {}
  // diagnostics = new FormControl();
  diagList: any = [];
  argTypes: any = []
  constructor(private httpClient: HttpClient, private modalService: NgbModal) {
  }
  ngOnInit() {
    this.scriptsLoad();
    this.getScriptNames()
    this.getDiagnosticScriptNames()
  }
  getScriptNames() {
    this.httpClient.get('/api/getScriptsFromPath').subscribe(data => {
      this.scriptsList = data;
    })
  }
  getDiagnosticScriptNames() {
    // let temp:any=[]
    this.httpClient.get('/api/getDiagnosticScriptsFromPath').subscribe(data => {
      this.diagList = data;
    })
  }
  applyFilter(filterValue: string) {
    this.dataSource.filter = filterValue.trim().toLowerCase();
    if (this.dataSource.paginator) {
      this.dataSource.paginator.firstPage();
    }
  }
  scriptsLoad() {
    this.accessList = []
    this.scriptsInfo = []
    this.scriptDropdown = []
    this.httpClient.get("/api/getAllIopsScripts").subscribe(data => {
      this.tempList = []
      this.tempList = data
      this.tempList.forEach(element => {
        this.scriptsInfo.push({ Selected: false, scriptName: element["scriptName"], scriptEdit: '', diagnostic_script: element['diagnostic_script'], diagnosticEdit: '' })
        this.scriptDropdown.push(true)
      });
      // Assign the data to the data source for the table to render
      this.dataSource = new MatTableDataSource(this.scriptsInfo)
      this.dataSource.paginator = this.paginator;
      this.dataSource.sort = this.sort;
    })
  }
  private selectAll() {
    this.scriptsInfo.forEach((item, index) => {
      item.Selected = this.selectedAll;
    });
  }
  private checkIfAllSelected() {
    this.selectedAll = this.scriptsInfo.every(function (item: any) {
      return item.Selected == true;
    });
  }
  addArguments(scriptName: any) {
    let content: any = ''
    this.httpClient.get('/api/getScriptContent/' + scriptName + '/' + 'main').subscribe(data => {
      if (data != 'Failure') {
        if (data == '') {
          alert("Script is empty")
        } else {
          content = data;
          let argList: any = {}
          let formdata = new FormData()
          formdata.append('Script', content)
          this.httpClient.post('/api/getArgumentsFromFile', formdata).subscribe(data => {
            let temp: any;
            temp = data
            temp.forEach(element => {
              argList[element] = this.argTypes[temp.indexOf(element)]
            });
            if (Object.keys(argList).length == 0) {
              argList = []
            }
            else if (argList.toLowerCase().includes('failure')) {
              argList = []
            }
            return argList;
          })
        }
      }
    })
  }
  save() {
    this.saveSuccess = false;
    let temp: any = []
    this.httpClient.get("/api/getAllIopsScripts").subscribe(data => {
      temp = data;
      this.scripts = []
      let selectedScripts = []
      let allScripts = []
      let duplicateStatus = true;
      this.dataSource.data.forEach(element => {
        if (element.Selected) {
          temp[this.dataSource.data.indexOf(element)] = element;
        }
      });
      let temp1 = []
      temp.forEach(element => {
        this.tempList.forEach(element1 => {
          if (element['scriptName'] == element1['scriptName']) {
            element['keyword'] = element1['keyword']
          }
          else {
            element['keyword'] = []
          }
        });
        element['arguments'] = this.addArguments(element['scriptName'])
        if (element.Selected) {
          temp1.push(element)
          this.scripts.push(element);
          selectedScripts.push(element['scriptName'])
        }
        delete element['Selected']
        allScripts.push(element['scriptName'])
      })
      temp1.forEach(element => {
        delete element['Selected']
        delete element['diagnosticEdit']
        delete element['scriptEdit']
      });
      let scr = allScripts;
      selectedScripts.forEach(element => {
        allScripts = scr
        if (allScripts.includes(element)) {
          let temp1 = allScripts.splice(allScripts.indexOf(element), 1)
          if (allScripts.includes(element)) {
            duplicateStatus = false;
          }
        }
      });
      let nameStatusList = []
      let diagnosticStatus = []
      if (this.scripts.length != 0) {
        this.scripts.forEach(item => {
          if (item['scriptName'].length == 0) {
            nameStatusList.push(false)
          } else if (item['diagnostic_script'].length == 0) {
            diagnosticStatus.push(false)
          }
        });
        if (nameStatusList.includes(false)) {
          alert("Script name is empty")
        } else if (diagnosticStatus.includes(false)) {
          alert("Diagnostic Script Name is empty")
        }
        else if (!duplicateStatus) {
          alert("Please remove duplicate script names")
        } else {
          let formData = new FormData();
          formData.append('Scripts', JSON.stringify(temp1));
          formData.append('Operation', 'Management')
          this.httpClient.post('/api/saveScriptDetails', formData, { responseType: 'text' }).subscribe(data => {
            alert(data)
            this.scriptsLoad()
            if (data == "Success") {
              this.message = "Please map the script in Micro-bot mapping !!!"
              this.saveSuccess = true
            }
          }, err => {
          });
        }
      } else {
        alert("Select atleast one")
      }
    })
  }
  Remove() {
    this.saveSuccess = false;
    let scriptNames = []
    this.dataSource.data.forEach(element => {
      if (element.Selected) {
        scriptNames.push(element['scriptName']);
      }
    })
    if (scriptNames.length == 0) {
      alert("Select atleast one")
    } else {
      let formData = new FormData()
      formData.append('Scripts', scriptNames.join(','));
      this.httpClient.post('/api/deleteiOpsScript', formData, { responseType: 'text' }).subscribe(data => {
        alert(data)
        this.scriptsLoad()
      })
    }
  }
  addElement() {
    this.saveSuccess = false;
    this.getScriptNames()
    this.scriptsInfo.push({ Selected: false, scriptName: '', scriptEdit: '', diagnostic_script: '', diagnosticEdit: '' })
    this.scriptDropdown.push(false)
    this.dataSource = new MatTableDataSource(this.scriptsInfo);
  }
  runEnvironmentChange(value: string, index: number) {
    if (value.toLowerCase() == "local") {
      this.accessList[index] = false
    } else {
      this.accessList[index] = true
    }
  }
  scriptNameSelect() {
    this.getScriptNames()
  }
  assignScript(value: any) {
    this.toBeEdittedScript = value;
  }
  editScript(script: any, type: any) {
    let editScript: any
    let args: any = [];
    if (type == 'main') {
      editScript = script
      this.httpClient.get('/api/getArguments/' + 'main' + '/' + editScript).subscribe(data => {
        Object.keys(data).forEach(element => {
          args.push(data[element])
        });
        args = args.toString()
      })
    } else {
      editScript = this.toBeEdittedScript
      this.httpClient.get('/api/getArguments/' + 'diagnostic' + '/' + editScript).subscribe(data => {
        Object.keys(data).forEach(element => {
          args.push(data[element])
        });
        args = args.toString()
      })
    }
    if (editScript.length != 0) {
      this.saveSuccess = false;
      this.httpClient.get('/api/getScriptContent/' + editScript + '/' + type).subscribe(data => {
        if (data != 'Failure') {
          if (data == '') {
            alert("Script is empty")
          } else {
            const modalRef = this.modalService.open(CreateScriptComponent, { size: 'lg', windowClass: 'app-modal-window', backdrop: false });
            modalRef.componentInstance.emitData.subscribe(($e) => {
              this.argTypes = $e
            })
            console.log(args)
            let dataPassToChild: any = {};
            dataPassToChild['Content'] = data;
            dataPassToChild['Args'] = args;
            dataPassToChild['Name'] = editScript;
            dataPassToChild['Type'] = type;
            (<CreateScriptComponent>modalRef.componentInstance).dataToTakeAsInput = dataPassToChild;
            modalRef.result.then((result) => {
              console.log(result);
            }).catch((result) => {
              console.log(result);
            });
          }
        }
      })
    }
  }
  createScript(type: any) {
    this.saveSuccess = false;
    const modalRef = this.modalService.open(CreateScriptComponent, { size: 'lg', windowClass: 'app-modal-window', backdrop: false });
    modalRef.componentInstance.emitData.subscribe(($e) => {
      this.argTypes = $e
    })
    let dataPassToChild: any = {};
    dataPassToChild['Type'] = type;
    (<CreateScriptComponent>modalRef.componentInstance).dataToTakeAsInput = dataPassToChild;
    modalRef.result.then((result) => {
      console.log(result);
    }).catch((result) => {
      console.log(result);
    });
  }
}