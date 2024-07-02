/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { LogsComponent } from '../logs/logs.component';
import { NgbModal, NgbActiveModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
@Component({
  selector: 'app-rpa-popup',
  templateUrl: './rpa-popup.component.html',
  styleUrls: ['./rpa-popup.component.scss']
})
export class RpaPopupComponent implements OnInit {
  scriptDetails: any;
  argValue: {};
  scriptType: string;
  logs: {};
  type: string;
  message: string;
  scriptStatus: boolean;
  @Input() dataToTakeAsInput: any;
  auditLogs: any=[];
  @Output() emitData = new EventEmitter();
  script: any;
  argTypes: any;
  argList: any={};
  argStatus: boolean;
  envList: any=['Local'];
  runTypeStatus: boolean;
  diagName: any;
  lst_1: string[];
  closeResult: string;
  sampleLst='inputType : List,    SampleInput : [1,2,3,"test"]';
  sampleDict: string='inputType : Dictionary,    SampleInput : {"test":123,"prod":"IIA"}';
  sampleBool='inputType : Boolean,    SampleInput : true';
  sampleStr='inputType : String,    SampleInput : Hello World!!!';
  sampleNum='inputType : Number,    SampleInput : 7';
  constructor(private httpClient: HttpClient, private modalService: NgbModal, public  activeModal:  NgbActiveModal) { }
  ngOnInit() {
    this.scriptType=this.dataToTakeAsInput['Type']
    this.scriptDetails=this.dataToTakeAsInput['ScriptDetails']
    this.getArgs();
    this.runTypeStatus=true;
  }
  getArgs(){
    if(this.scriptType=='diagnostic'){
      this.diagName=this.dataToTakeAsInput['DiagName']
      this.scriptDetails['diag_name']=this.diagName
      this.httpClient.get('/api/getRPA_Arguments/'+this.scriptType+'/'+this.scriptDetails['diag_name']+'/'+this.scriptDetails['incident_no']).subscribe(data=>{
        this.argList=data
        let tempDict = {}
        this.lst_1=Object.keys(this.argList)
        Object.keys(this.argList).forEach(key => {
          tempDict[key] = this.argList[key]["type"].toUpperCase();
        });
        this.argValue = tempDict;
        if (Object.keys(this.argList).length==0){
          this.argStatus=true;
        }
        else if(this.argList.toLowerCase().includes('failure')){
          alert(this.argList)
        }
      })
    }else{
      //use case for Reset Password
      console.log('scriptDetails...',this.scriptDetails);
      this.httpClient.get('/api/getRPA_Arguments/'+this.scriptType+'/'+this.scriptDetails['name']+'/'+this.scriptDetails['incident_no']).subscribe(data=>{
        this.argList=data
        let tempDict = {}
        this.lst_1=Object.keys(this.argList)
        Object.keys(this.argList).forEach(key => {
          tempDict[key] = this.argList[key]["type"].toUpperCase();
          console.log('param............',this.argList[key]["type"]);
        });
        this.argValue = tempDict;
        if (Object.keys(this.argList).length==0){
          this.argStatus=true;
        }
        else if(this.argList.toLowerCase().includes('failure')){
          alert(this.argList)
        }
      });
    }
  }
  argTypeSample(){
  }
  open(content) {
    this.modalService.open(content, { ariaLabelledBy: 'modal-basic-title', size: "lg" }).result.then((result) => {
      this.closeResult = 'Closed with: ${result}';
    });
  }
  showLogs(value:any){
    console.log(value)
    const modalRef = this.modalService.open(LogsComponent, { size: 'lg',backdrop:false});
    let dataPassToChild: any = {};
    dataPassToChild['Logs'] = this.logs;
    (<LogsComponent>modalRef.componentInstance).dataToTakeAsInput = dataPassToChild;
      modalRef.result.then((result) => {
        console.log(result);
      }).catch( (result) => {
        console.log(result);
      });
  }
  closeAlert(){
    this.scriptStatus=false;
  }
  SaveResolutionDetails(type:any,name:any,status:any,logs:any){
    let formdata=new FormData()
    formdata.append('Number',this.dataToTakeAsInput["IncidentNumber"])
    formdata.append('Description',this.dataToTakeAsInput["Description"])
    formdata.append('Type',type)
    formdata.append('Name',name)
    formdata.append('Status',status)
    formdata.append('Logs',logs)
    this.httpClient.post('/api/SaveResolutionDetails',formdata,{responseType:'text'}).subscribe(data=>{
      console.log(data)
    })
  }
  invokeResolution(){
    let ScriptName:any;
    if(this.scriptDetails['type']=='RPA'){
      console.log('argvalue..................',this.argValue)
      if (Object.keys(this.argValue).length!=0){
        alert("Execution Started!!! Please wait for its completion.")
        if(this.scriptType=='RPA'){
          ScriptName=this.scriptDetails["name"]
        }else{
          ScriptName=this.scriptDetails["diag_name"]
        }
          this.logs={}
          let formData = new FormData();
          formData.append('ScriptName', ScriptName);
          // formData.append('Arguments', JSON.stringify(argumentsList[item["label"]]));
          formData.append('Environment',this.scriptDetails["environment"])
          formData.append('Type',this.scriptType)
          formData.append('Args',JSON.stringify(this.argValue))
          console.log('Args....................',this.argValue)
          this.httpClient.post("/api/invokeRPA1", formData, {responseType:'text'}).subscribe(data=>{
            this.logs[this.scriptDetails["name"]]=data;
            this.type = 'success'; 
            this.message = "Operation Completed"; 
            this.scriptStatus=true;
          if (!(data.toLowerCase().includes('exception')) && !(data.toLowerCase().includes('err')) && !(data.toLowerCase().includes('error')) && !(data.toLowerCase().includes('access denied'))){
            if(this.scriptType=='RPA'){
              this.SaveResolutionDetails(this.scriptDetails['type'],ScriptName,'success','Running Bot : '+data)
            }else{
              this.SaveResolutionDetails(this.scriptDetails['type'],ScriptName,'success','Running Diagnostic Bot : '+data)
            }
          }else{
            if(this.scriptType=='RPA'){
              this.SaveResolutionDetails(this.scriptDetails['type'],ScriptName,'failure','Running Bot : '+data) 
            }else{
              this.SaveResolutionDetails(this.scriptDetails['type'],ScriptName,'failure','Running Diagnostic Bot : '+data) 
            }
            }
          this.httpClient.get('/api/getAuditLogs/'+this.dataToTakeAsInput["IncidentNumber"]).subscribe(data=>{
            this.auditLogs=data;
            this.auditLogs.reverse()
            this.emitData.next(this.auditLogs);
          })
        })
      }
      }else{
        alert('Provide all Arguments')
      }   
  }
}
