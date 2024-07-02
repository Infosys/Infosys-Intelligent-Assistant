/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit, Input } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { NgForm } from '@angular/forms';
import { ActivatedRoute, ParamMap } from '@angular/router';
import { switchMap } from 'rxjs/operators';
import { NgbModal, NgbActiveModal,ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
import { PopupModelComponent } from '../../popup-model/popup-model.component';
import { Router } from '@angular/router';
import { TuningOptionComponent } from '../tuning-option/tuning-option.component';
@Component({
  selector: 'algorithm-information',
  templateUrl: './algorithm-information.component.html',
  styleUrls: ['./algorithm-information.component.css']
})
export class AlgorithmInformationComponent implements OnInit {
  algorithmChosen: boolean = false;
  customerId: number = 1;
  predictedFieldsInformation: any = [];
  algorithmsInformation: any = [];
  approvedPredictedFieldsInformation: any = [];
  approvedAlgorithmsInformation: any = [];
  accuracies: any = [];
  saveAlgorithmInformation = [];
  @Input() trainingId: number;
  predFields: any;
  approvedAlgorithms: boolean = false;
  saveSuccess: boolean = false;
  inProgressAlgorithms: boolean = false;
  bestAccuracies: any = [];
  chosenAlgorithmName: any = [];
  datasetID: number;
  tunedAlgorithms: boolean;
  tunedPredictedFieldsInformation: any;
  tunedAlgorithmsInformation: any;
  constructor(private httpClient: HttpClient, private route: ActivatedRoute,private modalService: NgbModal, private router: Router) {
  }
  ngOnInit() {
    this.datasetID = + this.route.snapshot.paramMap.get('datasetID');
    this.showAlgorithms();
  }
  showAlgorithms() {
    this.algorithmChosen = true;
    this.predictedFieldsInformation = [];
    this.algorithmsInformation = [];
    this.httpClient.get('/api/algorithms/' + this.customerId + "/" + this.datasetID + "/InProgress").subscribe(data => {
      this.inProgressAlgorithms = true;
      if(data && data['PredictedFields'] != "") {
        this.predFields= data['PredictedFields'];
        this.predictedFieldsInformation = data['PredictedFields'];
        this.predictedFieldsInformation.forEach((predictedField, index) => {
          this.algorithmsInformation.push(predictedField['Algorithms']);
          let predictedfieldAlgoAccuracies = [];
          this.algorithmsInformation[index].forEach(algorithm => {
            predictedfieldAlgoAccuracies.push({'AlgorithmName': algorithm.AlgorithmName, 'F1_score' : algorithm.F1_score});
          });
          let max = predictedfieldAlgoAccuracies[0]['F1_score'];
          let bestAlgorithmName = predictedfieldAlgoAccuracies[0]['AlgorithmName'];
          predictedfieldAlgoAccuracies.forEach(algoAccuracy => {
            if (algoAccuracy['F1_score'] > max) {
              max = algoAccuracy['F1_score'];
              bestAlgorithmName = algoAccuracy['AlgorithmName'];
            }
          });
          this.bestAccuracies[predictedField['Name']] = {'AlgorithmName': bestAlgorithmName, 'F1_score' : max};
          this.saveAlgorithmInformation.push({'PredictedFieldName': predictedField['Name'], 'AlgorithmName': bestAlgorithmName});
        });
      } else {
        this.inProgressAlgorithms = false;
      }
    })
    this.httpClient.get('/api/algorithms/' + this.customerId + "/" + this.datasetID + "/Approved").subscribe(data => {
      if(data && data['PredictedFields'] != "") {
        this.approvedAlgorithms = true;
        this.approvedPredictedFieldsInformation = data['PredictedFields'];
        this.approvedPredictedFieldsInformation.forEach(approvedPredictedField => {
          this.approvedAlgorithmsInformation.push(approvedPredictedField['Algorithms']);
          this.httpClient.get('/api/chosenAlgorithms/' + this.customerId + "/" + this.datasetID + "/Approved").subscribe(data => {
            let temp = data['PredictedFields'];
            temp.forEach(x => {
              if(approvedPredictedField['Name'] == x.PredictedFieldName)
              this.chosenAlgorithmName[approvedPredictedField['Name']] = x.AlgorithmName;
            });
          });
        });
      } else {
        this.approvedAlgorithms = false;
      }
    })
    if (this.predFields == null || this.predFields.length == 0) {
      this.httpClient.get('/api/algorithms/' + this.customerId + "/" + this.datasetID + "/Approved").subscribe(data => {
        if (data && data['PredictedFields'] != "") {
          this.predFields = data['PredictedFields'];
        }
      });
    }
  }
  chooseAlgorithm(predictedFieldName: string, algoName: string) {
    this.saveSuccess = false;
    this.saveAlgorithmInformation.forEach((predictedField, index) => {
      if(predictedField['PredictedFieldName'] == predictedFieldName) {
        this.saveAlgorithmInformation.splice(index, 1);
      }
    })
    this.saveAlgorithmInformation.push({'PredictedFieldName': predictedFieldName, 'AlgorithmName': algoName});
  }
  useCurrent() {
    this.httpClient.put('/api/updateUserPreference/' + this.customerId + "/" + this.datasetID + "/Approved", this.saveAlgorithmInformation, { responseType: 'text' })
      .subscribe(msg => {
        this.saveSuccess = true;
        console.log(msg);
      },
      err => {
        console.log(err);
        throw "";
      });
  }
  useSystem() {
    this.httpClient.put('/api/updateUserPreference/' + this.customerId + "/" + this.datasetID + "/Discarded", null, { responseType: 'text' })
      .subscribe(msg => {
        console.log(msg);
      },
      err => {
        console.log(err);
        throw "";
      });
  }
  openModel(predictedFileldName: string, algorithmName: string, trainingStatus: string){
    if(predictedFileldName && algorithmName){
      this.httpClient.get('/api/getClassificationReport/' + this.customerId +'/'+ this.datasetID +'/'+ predictedFileldName + '/' + algorithmName +'/'+ trainingStatus)
      .subscribe(classificationReport =>{
        if(!classificationReport['failure']){
          const modalRef = this.modalService.open(PopupModelComponent, {ariaLabelledBy: 'modal-basic-title'});
          modalRef.componentInstance.algorithmsInformation=classificationReport;
        }else{
          alert(classificationReport['failure']);
        }
      });
    }else{
      alert("some values are missing. Can't perform this operation");
    }
  }
  OpenTuningPage(){
    this.router.navigate(['/algorithmfilter/', this.datasetID]);
  }
  openAdvancedSettingModal(){
    const modalRef = this.modalService.open(TuningOptionComponent, { ariaLabelledBy: 'modal-basic-title', size: "lg" });
    modalRef.componentInstance.closeResult = true;
    modalRef.componentInstance.tagCloudData = [];
    modalRef.componentInstance.Summaries = [];
    modalRef.componentInstance.customerId = this.customerId;
    modalRef.componentInstance.datasetID = this.datasetID;
    if (this.predFields != null && this.predFields.length > 0) {
      this.predFields.forEach(element => {
        modalRef.componentInstance.Summaries.push(element.Name.toString());
      });
      modalRef.componentInstance.predicted_field = this.predFields[0].Name.toString();
      modalRef.componentInstance.drawGraph();
    }
  }
}