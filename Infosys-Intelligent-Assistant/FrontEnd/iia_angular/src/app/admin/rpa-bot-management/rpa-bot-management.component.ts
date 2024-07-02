/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { HttpClient } from '@angular/common/http';
import { Component, Input, OnInit, ViewChild } from '@angular/core';
import { NgbModal, NgbActiveModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
import { CreateRPAComponent } from '../create-rpa/create-rpa.component';
import { MatPaginator, MatSort, MatTableDataSource } from '@angular/material';
import { forEach } from '@angular/router/src/utils/collection';
export interface DataFromUser {
  Selected: any;
  scriptName: string;
  scriptEdit: string;
  diagnostic_script: string;
  diagnosticEdit: string;
}
@Component({
  selector: 'app-rpa-bot-management',
  templateUrl: './rpa-bot-management.component.html',
  styleUrls: ['./rpa-bot-management.component.scss']
})
export class RPABotManagementComponent implements OnInit {
  saveSuccess: boolean;
  argTypes: any = [];
  public scriptsInfo: DataFromUser[] = [];
  scriptDropdown = [];
  dataSource: MatTableDataSource<DataFromUser>;
  displayedColumns: string[] = ['Selected', 'scriptName', 'scriptEdit', 'diagnostic_script', 'diagnosticEdit'];
  selectedAll: any;
  scriptsList: any = [];
  scripts: any[];
  tempList: any;
  accessList: any[];
  @ViewChild(MatPaginator) paginator: MatPaginator;
  @ViewChild(MatSort) sort: MatSort;
  message: string;
  toBeEdittedScript: any;
  diagList: Object;
  constructor(private httpClient: HttpClient, private modalService: NgbModal) { }
  ngOnInit() {
    this.scriptsLoad();
    this.getScriptNames();
    this.getDiagnosticRPANames();
  }
  getDiagnosticRPANames() {
    this.httpClient.get('/api/getDiagnosticRPAFromPath').subscribe(data => {
      this.diagList = data;
    })
  }
  createScript(type: any) {
    this.saveSuccess = false;
    const modalRef = this.modalService.open(CreateRPAComponent, { size: 'lg', windowClass: 'app-modal-window', backdrop: false });
    let dataPassToChild: any = {};
    dataPassToChild['Type'] = type;
    (<CreateRPAComponent>modalRef.componentInstance).dataToTakeAsInput = dataPassToChild;
    modalRef.result.then((result) => {
      console.log(result);
    }).catch((result) => {
      console.log(result);
    });
  }
  getScriptNames() {
    this.httpClient.get('/api/getRPAFromPath').subscribe(data => {
      this.scriptsList = data;
    })
  }
  assignScript(value: any) {
    this.toBeEdittedScript = value;
  }
  addElement() {
    this.saveSuccess = false;
    this.getScriptNames()
    this.scriptsInfo.push({ Selected: false, scriptName: '', scriptEdit: '', diagnostic_script: '', diagnosticEdit: '' })
    this.scriptDropdown.push(false)
    this.dataSource = new MatTableDataSource(this.scriptsInfo);
  }
  scriptNameSelect() {
    this.getScriptNames()
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
  save2() {
    this.saveSuccess = false;
    let temp: any = [];
    let testVarList = {};
    this.httpClient.get("/api/getAllRPAConfig1").subscribe(data => {
      temp = data;
      this.scripts = []
      let selectedScripts = []
      let allScripts = []
      let duplicateStatus = true;
      let scriptName;
      this.dataSource.data.forEach(element => {
        if (element.Selected) {
          temp[this.dataSource.data.indexOf(element)] = element;
          scriptName = element.scriptName;
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
        if (element.Selected) {
          if (testVarList[element['scriptName']].length == 0) {
            element["keyword"] = []
          } else if (testVarList[element['scriptName']] instanceof Array) {
            element["keyword"] = testVarList[element['scriptName']][0].split(',')
          } else {
            element["keyword"] = testVarList[element['scriptName']].split(',')
          }
          temp1.push(element)
          this.scripts.push(element);
          selectedScripts.push(element['scriptName'])
        }
        delete element['Selected']
        allScripts.push(element['scriptName'])
      });
      temp1.forEach(element => {
        delete element['Selected']
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
      if (this.scripts.length != 0) {
        this.scripts.forEach(item => {
          if (item['scriptName'].length == 0) {
            nameStatusList.push(false)
          }
        });
        if (nameStatusList.includes(false)) {
          alert("Script name is empty")
        }
        else if (!duplicateStatus) {
          alert("Please remove duplicates")
        } else {
          let formData = new FormData();
          formData.append('Scripts', JSON.stringify(temp1));
          this.httpClient.post('/api/saveRPADetails', formData, { responseType: 'text' }).subscribe(data => {
            this.scriptsLoad()
            if (data == "Success") {
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
  save1() {
    let temp: any = []
    this.httpClient.get("/api/getAllRPAConfig1").subscribe(data => {
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
        if (element.Selected) {
          if (element['keyword'].length == 0) {
            element["keyword"] = []
          } else if (element["keyword"] instanceof Array) {
            element["keyword"] = element["keyword"]
          } else {
            element["keyword"] = element["keyword"].split(',')
          }
          temp1.push(element)
          this.scripts.push(element);
          selectedScripts.push(element['scriptName'])
        }
        delete element['Selected']
        allScripts.push(element['scriptName'])
      })
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
      let keywordsStatusList = []
      if (this.scripts.length != 0) {
        this.scripts.forEach(item => {
          if (item['scriptName'].length == 0) {
            nameStatusList.push(false)
          } else if (item['keyword'].length == 0) {
            keywordsStatusList.push(false)
          }
        });
        if (nameStatusList.includes(false)) {
          alert("Script name is empty")
        } else if (keywordsStatusList.includes(false)) {
          alert("keywords are empty")
        } else if (!duplicateStatus) {
          alert("Please remove duplicate script names")
        } else {
          let formData = new FormData();
          formData.append('Scripts', JSON.stringify(temp1));
          formData.append('Operation', 'Mapping')
          this.httpClient.post('/api/saveRPADetails', formData, { responseType: 'text' }).subscribe(data => {
            this.scriptsLoad()
          }, err => {
          });
        }
      } else {
        alert("Select atleast one")
      }
    })
  }
  save() {
    this.saveSuccess = false;
    let temp: any = []
    this.httpClient.get("/api/getAllRPAConfig1").subscribe(data => {
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
          this.httpClient.post('/api/saveRPADetails', formData, { responseType: 'text' }).subscribe(data => {
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
  scriptsLoad() {
    this.accessList = []
    this.scriptsInfo = []
    this.scriptDropdown = []
    this.httpClient.get("/api/getAllRPAConfig1").subscribe(data => {
      this.tempList = []
      this.tempList = data
      this.tempList.forEach(element => {
        this.scriptsInfo.push({ Selected: false, scriptName: element["scriptName"], scriptEdit: '', diagnostic_script: element["diagnostic_script"], diagnosticEdit: '' })
        this.scriptDropdown.push(true)
      });
      // Assign the data to the data source for the table to render
      this.dataSource = new MatTableDataSource(this.scriptsInfo)
      this.dataSource.paginator = this.paginator;
      this.dataSource.sort = this.sort;
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
      this.httpClient.post('/api/deleteRPAFile', formData, { responseType: 'text' }).subscribe(data => {
        this.scriptsLoad()
      })
    }
  }
  applyFilter(filterValue: string) {
    this.dataSource.filter = filterValue.trim().toLowerCase();
    if (this.dataSource.paginator) {
      this.dataSource.paginator.firstPage();
    }
  }
  editScript(script: any, type: any) {
    let editScript: any
    let RpaType: any;
    if (type == 'RPA') {
      editScript = script
      RpaType = editScript.split('_')[0];
    } else if (type == 'diagnostic') {
      editScript = this.toBeEdittedScript
      RpaType = editScript.split('_')[0];
    }
    if (editScript.length != 0) {
      this.saveSuccess = false;
      this.httpClient.get('/api/getRPAContent/' + editScript + '/' + type).subscribe(data => {
        if (data != 'Failure') {
          if (data == '') {
            alert("Config is empty")
          } else {
            const modalRef = this.modalService.open(CreateRPAComponent, { size: 'lg', windowClass: 'app-modal-window', backdrop: false });
            let dataPassToChild: any = {};
            dataPassToChild['Content'] = data;
            dataPassToChild['Name'] = editScript;
            dataPassToChild['RpaType'] = RpaType
            dataPassToChild['Type'] = type;
            (<CreateRPAComponent>modalRef.componentInstance).dataToTakeAsInput = dataPassToChild;
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
}