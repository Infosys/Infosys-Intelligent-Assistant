/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit, Input } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute, ParamMap } from '@angular/router';
import { NgbModal, NgbActiveModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
import { PopupModelComponent } from '../popup-model/popup-model.component';
import { toInteger } from '@ng-bootstrap/ng-bootstrap/util/util';
import { Router } from '@angular/router';
@Component({
  selector: 'app-retraining',
  templateUrl: './retraining.component.html',
  styleUrls: ['./retraining.component.css']
})
export class RetrainingComponent implements OnInit {
  approvedAlgorithms: boolean = false;
  saveSuccess: boolean = false;
  algorithmChosen: boolean = false;
  trainedAlgorithms: boolean = false;
  loader = false;
  customerId: number = 1;
  predictedFieldsInformation: any = [];
  algorithmsInformation: any = [];
  approvedPredictedFieldsInformation: any = [];
  approvedAlgorithmsInformation: any = [];
  accuracies: any = [];
  saveAlgorithmInformation = [];
  @Input() trainingId: number;
  bestAccuracies: any = [];
  chosenAlgorithmName: any = [];
  datasetID: number;
  chosenTeam: string;
  teams: any = [];
  totalCount: number;
  currentTeam: string;
  teamId: number;
  saveFailure: boolean = false;
  prdictedFieldName: string;
  retrainedAlgorithName: string;
  fieldsToBeSaved = [];
  RetrainTableFlag: boolean = false;
  ConfigFlag: boolean = false;
  maxUntrained: number;
  timeInterval: number;
  CreateJobFlag: boolean = false;
  JobSuccessFlag: boolean = false;
  datasetExists: boolean = false;   // new
  retrain_date: string = '';
  click: boolean = false;
  constructor(private httpClient: HttpClient, private route: ActivatedRoute, private modalService: NgbModal, private router: Router) {
    this.saveSuccess = false;
    this.saveFailure = false;
    this.httpClient.get('/api/getDatasetTeamNames/' + this.customerId).subscribe(data => {
      if (data['Teams'].length > 0) {
        this.datasetExists = true;
        //this.teams = data['Teams'];
        console.log('data from getdatasetteamnames methods: ' + data['Teams'] + data['DatasetIDs'])
        this.chosenTeam = data['Teams'][0];
        this.datasetID = data['DatasetIDs'][0];
        this.showAlgorithms();
        this.httpClient.get('/api/getTeams/' + this.customerId).subscribe(data => {
          this.teams = data['Teams'];
          console.log(this.teams);
          this.getConfigDetails();
        });
      }
    });
    //this.ConfigFlag = true;
  }
  ngOnInit() {
  }
  private getConfigDetails() {
    this.httpClient.get('/api/getJobSettings/' + this.customerId + '/' + this.datasetID, { responseType: 'text' })
      .subscribe(data => {
        console.log("Config present...");
        if (data == "success") {
          console.log("Config present.1..");
          this.RetrainTableFlag = true;
          this.ConfigFlag = false;
        }
        else {
          console.log("Config not present...")
          this.ConfigFlag = true;
          this.RetrainTableFlag = false;
        }
      })
  }
  saveJobSettings() {
    if (this.retrain_date.trim() == '' && this.timeInterval == undefined && this.maxUntrained == undefined) {
      alert('Please Enter All the Mandatory Fields');
      return;
    }
    if (this.retrain_date.trim() == '') {
      alert('Please Select Date');
      return;
    }
    if (this.timeInterval == undefined) {
      alert('Please Enter TimeInterval');
      return;
    }
    if (this.maxUntrained == undefined) {
      alert('Please Enter MinUntrained value');
      return;
    }
    this.httpClient.get('/api/getTeamID/' + this.customerId + "/" + this.chosenTeam).subscribe(data => {
      this.teamId = parseInt(data.toString());;
      console.log("team" + this.teamId)
      this.httpClient.get('/api/getDatasetID/' + this.customerId + "/" + this.teamId, { responseType: 'text' }).subscribe(data => {
        this.datasetID = parseInt(data.toString());
        if (this.datasetID == -1) {
          // go back to some dataset addition screen logic
          console.log("do nothing");
          this.datasetExists = false;
        }
        else {
          var settings = {}
          this.timeInterval = this.timeInterval * 24 * 60 * 60;
          settings['TimeInterval'] = Number(this.timeInterval)
          settings['MinUntrained'] = Number(this.maxUntrained)
          settings['DatasetID'] = this.datasetID
          settings['retrain_date'] = this.retrain_date
          this.httpClient.post('/api/CreateJob/' + this.customerId, [settings], { responseType: 'text' })
            .subscribe(resp => {
              if (resp == "success") {
                console.log(data)
                console.log("Job Created Successfully")
                this.JobSuccessFlag = true;
                this.click = !this.click;
              }
              else {
                console.log('Some error occured in creating the Job');
                alert('Please enter all the Mandatory Fields');
              }
            })
        }
      });
    });
  }
  teamChange() {
    this.httpClient.get('/api/getTeamID/' + this.customerId + '/' + this.chosenTeam).subscribe(data => {
      if (data != 'failure') {
        this.loader = true;
        this.teamId = Number(data);
        console.log("team id..." + this.teamId);
        this.httpClient.get('/api/getDatasetID/' + this.customerId + '/' + this.teamId).subscribe(data => {
          if (data != '-1') {
            this.datasetID = Number(data);
            this.datasetExists = true;
            console.log("dataset id..." + this.datasetID);
            this.httpClient.get('/api/getJobSettings/' + this.customerId + '/' + this.datasetID, { responseType: 'text' })
              .subscribe(resp => {
                this.loader = false;
                if (resp == "success") {
                  this.RetrainTableFlag = true;
                  this.ConfigFlag = false;
                  this.showAlgorithms();
                }
                else {
                  this.RetrainTableFlag = false;
                  this.ConfigFlag = true;
                }
              })
          } else {
            this.loader = false;
            console.log('No data found from teams colletion!')
            this.trainedAlgorithms = false;
            this.approvedAlgorithms = false;
            this.approvedAlgorithmsInformation = [];
            this.datasetExists = false;
            this.RetrainTableFlag = false;
            this.ConfigFlag = true;
            //this.router.navigate(['../training']);
          }
        });
      } else {
        console.log('No data found from teams colletion!')
      }
    });
  }
  showAlgorithms() {
    this.algorithmChosen = true;
    this.predictedFieldsInformation = [];
    this.algorithmsInformation = [];
    this.httpClient.get('/api/algorithms/' + this.customerId + "/" + this.datasetID + "/Retraining").subscribe(data => {
      this.trainedAlgorithms = true;
      console.log('in showAlgorithms');
      if (data && data['PredictedFields'] != "") {
        this.predictedFieldsInformation = data['PredictedFields'];
        this.predictedFieldsInformation.forEach((predictedField, index) => {
          this.algorithmsInformation.push(predictedField['Algorithms']);
          let predictedfieldAlgoAccuracies = [];
          this.algorithmsInformation[index].forEach(algorithm => {
            predictedfieldAlgoAccuracies.push({ 'AlgorithmName': algorithm.AlgorithmName, 'F1_score': algorithm.F1_score });
          });
          let max = predictedfieldAlgoAccuracies[0]['F1_score'];
          let bestAlgorithmName = predictedfieldAlgoAccuracies[0]['AlgorithmName'];
          predictedfieldAlgoAccuracies.forEach(algoAccuracy => {
            if (algoAccuracy['F1_score'] > max) {
              max = algoAccuracy['F1_score'];
              bestAlgorithmName = algoAccuracy['AlgorithmName'];
            }
          });
          this.bestAccuracies[predictedField['Name']] = { 'AlgorithmName': bestAlgorithmName, 'F1_score': max };
          this.saveAlgorithmInformation.push({ 'PredictedFieldName': predictedField['Name'], 'AlgorithmName': bestAlgorithmName });
          this.prdictedFieldName = predictedField['Name'];
          this.retrainedAlgorithName = bestAlgorithmName;
          this.fieldsToBeSaved.push({ 'PredictedFieldName': this.prdictedFieldName, 'AlgorithmName': this.retrainedAlgorithName })
        });
        this.fieldsToBeSaved.forEach(document => {
          console.log('this.fieldsToBeSaved: ' + document['PredictedFieldName'] + ': ' + document['AlgorithmName']);
        });
      } else {
        this.trainedAlgorithms = false;
      }
      
    })//end of api call
    this.approvedAlgorithmsInformation = [];
    this.httpClient.get('/api/algorithms/' + this.customerId + "/" + this.datasetID + "/Approved").subscribe(data => {
      if (data && data['PredictedFields'] != "") {
        this.approvedAlgorithms = true;
        this.approvedPredictedFieldsInformation = data['PredictedFields'];
        this.approvedPredictedFieldsInformation.forEach(approvedPredictedField => {
          this.approvedAlgorithmsInformation.push(approvedPredictedField['Algorithms']);
          this.httpClient.get('/api/chosenAlgorithms/' + this.customerId + "/" + this.datasetID + "/Approved").subscribe(data => {
            
            let temp = data['PredictedFields'];
            temp.forEach(x => {
              if (approvedPredictedField['Name'] == x.PredictedFieldName)
                this.chosenAlgorithmName[approvedPredictedField['Name']] = x.AlgorithmName;
            });
            
          });
        });//end of api call
      } else {
        this.approvedAlgorithms = false;
      }
      
    })//end of api call
  }
  useRetrained() {
    this.httpClient.put('/api/updateRetrainPreference/' + this.customerId + "/" + this.datasetID + "/Approved", this.fieldsToBeSaved, { responseType: 'text', headers: { 'Content-Type': 'application/json' } })
      .subscribe(msg => {
        if (msg == "success") {
          this.saveFailure = false;
          this.saveSuccess = true;
          console.log(msg);
        } else {
          this.saveSuccess = false;
          this.saveFailure = true;
          console.log(msg);
        }
      },
        err => {
          console.log(err);
          throw "";
        });
  }
  openModel(predictedFileldName: string, algorithmName: string, trainingStatus: string) {
    if (predictedFileldName && algorithmName) {
      this.httpClient.get('/api/getClassificationReport/' + this.customerId + '/' + this.datasetID + '/' + predictedFileldName + '/' + algorithmName + '/' + trainingStatus)
        .subscribe(classificationReport => {
          if (!classificationReport['failure']) {
            
            const modalRef = this.modalService.open(PopupModelComponent, { ariaLabelledBy: 'modal-basic-title', size: "lg" });
            modalRef.componentInstance.algorithmsInformation = classificationReport;
          } else {
            
            alert(classificationReport['failure']);
          }
        });
    } else {
      alert("some values are missing. Can't perform this operation");
    }
  }
  chooseAlgorithm(predictedFieldName: string, algorithmName: string) {
    
    this.fieldsToBeSaved.forEach(document => {
      if (document['PredictedFieldName'] == predictedFieldName) {
        document['AlgorithmName'] = algorithmName;
      }
    });
    this.fieldsToBeSaved.forEach(document => {
      
    });
  }
}
