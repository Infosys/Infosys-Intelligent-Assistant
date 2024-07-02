/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute, ParamMap } from '@angular/router';
import { Router } from '@angular/router';
import { NgbModal, NgbActiveModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
import { TuningOptionComponent } from '../tuning-option/tuning-option.component'
import { BrowserAnimationsModule } from '@angular/platform-browser/animations'; // this is needed!
import { PopupModelComponent } from '../../popup-model/popup-model.component';
@Component({
  selector: 'app-algorithm-filter',
  templateUrl: './algorithm-filter.component.html',
  styleUrls: ['./algorithm-filter.component.css']
})
export class AlgorithmFilterComponent implements OnInit {
  private customerId: number = 1;
  RFCTrainingMode: string = "Single";
  RFCTrainingModeDepth: string = "Single";
  XGBTrainingMode: string = "Single";
  SVCTrainingMode: string = "Single";
  NBTrainingMode: string = "Single";
  LRTrainingMode: string = "Single";
  defaultRFCParameters: any = [];
  defaultXGBParameters: any = [];
  defaultSVCParameters: any = [];
  defaultLRParameters: any = [];
  defaultNBParameters: any = [];
  tuningStatus: string = "Default";
  datasetID: number;
  predictedFieldsInformation: any = [];
  tunedPredictedFieldsInformation: any = [];
  algorithmsInformation: any = [];
  tunedAlgorithmsInformation: any = [];
  tunedAlgorithms: boolean = false;
  algorithmChosen: boolean = false;
  inProgressAlgorithms: boolean = false;
  tuneLoading: boolean = false;
  minRFC: number;
  maxRFC: number;
  pointsRFC: number;
  RFCCriterionValues: any = [];
  minXGB: number;
  maxXGB: number;
  pointsXGB: number;
  XGBObjectiveValues: any = [];
  minSVC: number;
  maxSVC: number;
  pointsSVC: number;
  SVCKernelValues: any = [];
  minNB: number;
  maxNB: number;
  pointsNB: number;
  minLR: number;
  maxLR: number;
  pointsLR: number;
  closeResult: string;
  predFields: any = [];
  trainingMode = 'IIA';
  datasetExists = false;
  numberFormat: any;
  parameterValue: number;
  ParameterValue: number;
  parameterLR: number;
  parameterNB: number;
  parameterSVC: number;
  parameterXGB: number;
  parameterMax: number;
  status: number = 0;
  Value: number
  parameter: any;
  constructor(private httpClient: HttpClient, private route: ActivatedRoute, private router: Router, private modalService: NgbModal) {
    this.datasetID = + this.route.snapshot.paramMap.get('datasetID');
    this.getDefaultParameters("Single", "all");
    this.showAlgorithms();
  }
  ngOnInit() {
  }
  private getDefaultParameters(parameterType: string, algoName: string) {
    this.httpClient.get('/api/getDatasetDetails/' + this.customerId + "/" + this.datasetID).subscribe(dataa => {
      if (dataa && dataa['name'] === "") {
        this.datasetExists = false;
      } else {
        this.trainingMode = dataa['training_mode'];
        this.datasetExists = true;
      }
    });
    this.httpClient.get('/api/getAlgoDefaultParams/' + this.customerId + "/" + this.datasetID + "/" + parameterType).subscribe(data => {
      let temp = data['Algorithms'];
      if (algoName == "RandomForestClassifier") {
        temp.forEach(algorithm => {
          if (algorithm['AlgorithmName'] == "RandomForestClassifier") {
            this.defaultRFCParameters = algorithm['Parameters'];
            this.httpClient.get('/api/getDropdownParams/' + algorithm['AlgorithmName']).subscribe(data => {
              if (data && data['ParameterName'] == "criterion") {
                this.RFCCriterionValues = data['Value'];
              }
            });
          }
        });
      } else if (algoName == "XGBClassifier") {
        temp.forEach(algorithm => {
          if (algorithm['AlgorithmName'] == "XGBClassifier") {
            this.defaultXGBParameters = algorithm['Parameters'];
            this.httpClient.get('/api/getDropdownParams/' + algorithm['AlgorithmName']).subscribe(data => {
              if (data && data['ParameterName'] == "objective") {
                this.XGBObjectiveValues = data['Value'];
              }
            });
          }
        });
      } else if (algoName == "SVC") {
        temp.forEach(algorithm => {
          if (algorithm['AlgorithmName'] == "SVC") {
            this.defaultSVCParameters = algorithm['Parameters'];
            this.httpClient.get('/api/getDropdownParams/' + algorithm['AlgorithmName']).subscribe(data => {
              if (data && data['ParameterName'] == "kernel") {
                this.SVCKernelValues = data['Value'];
              }
            });
          }
        });
      } else if (algoName == "MultinomialNB") {
        temp.forEach(algorithm => {
          if (algorithm['AlgorithmName'] == "MultinomialNB") {
            this.defaultNBParameters = algorithm['Parameters'];
          }
        });
      } else if (algoName == "LogisticRegression") {
        temp.forEach(algorithm => {
          if (algorithm['AlgorithmName'] == "LogisticRegression") {
            this.defaultLRParameters = algorithm['Parameters'];
          }
        });
      } else if (algoName == "all") {
        temp.forEach(algorithm => {
          if (algorithm['AlgorithmName'] == "RandomForestClassifier") {
            this.defaultRFCParameters = algorithm['Parameters'];
            this.httpClient.get('/api/getDropdownParams/' + algorithm['AlgorithmName']).subscribe(data => {
              if (data && data[0]['ParameterName'] == "criterion") {
                this.RFCCriterionValues = data[0]['Value'];
              }
            });
          } else if (algorithm['AlgorithmName'] == "XGBClassifier") {
            this.defaultXGBParameters = algorithm['Parameters'];
            this.httpClient.get('/api/getDropdownParams/' + algorithm['AlgorithmName']).subscribe(data => {
              if (data && data[0]['ParameterName'] == "objective") {
                this.XGBObjectiveValues = data[0]['Value'];
              }
            });
          } else if (algorithm['AlgorithmName'] == "SVC") {
            this.defaultSVCParameters = algorithm['Parameters'];
            this.httpClient.get('/api/getDropdownParams/' + algorithm['AlgorithmName']).subscribe(data => {
              if (data && data[0]['ParameterName'] == "kernel") {
                this.SVCKernelValues = data[0]['Value'];
              }
            });
          } else if (algorithm['AlgorithmName'] == "MultinomialNB") {
            this.defaultNBParameters = algorithm['Parameters'];
          } else if (algorithm['AlgorithmName'] == "LogisticRegression") {
            this.defaultLRParameters = algorithm['Parameters'];
          }
        });
      }
    });
  }
  private modeChangeRFC(parameterType: string) {
    this.defaultRFCParameters = [];
    this.getDefaultParameters(parameterType, "RandomForestClassifier");
  }
  private modeChangeXGB(parameterType: string) {
    this.defaultXGBParameters = [];
    this.getDefaultParameters(parameterType, "XGBClassifier");
  }
  private modeChangeLR(parameterType: string) {
    this.defaultLRParameters = [];
    this.getDefaultParameters(parameterType, "LogisticRegression");
  }
  private modeChangeNB(parameterType: string) {
    this.defaultNBParameters = [];
    this.getDefaultParameters(parameterType, "MultinomialNB");
  }
  private modeChangeSVC(parameterType: string) {
    this.defaultSVCParameters = [];
    this.getDefaultParameters(parameterType, "SVC");
  }
  private chooseTuning(status: string) {
    this.tuningStatus = status;
  }
  private onSubmit() {
    this.httpClient.get('/api/algoConfiguration/' + this.customerId + "/" + this.datasetID + "/" + this.tuningStatus).subscribe(data => {
      this.router.navigate(['/algorithminformation', this.datasetID]);
    });
  }
  private showAlgorithms() {
    this.algorithmChosen = true;
    this.predictedFieldsInformation = [];
    this.algorithmsInformation = [];
    this.httpClient.get('/api/algorithms/' + this.customerId + "/" + this.datasetID + "/InProgress").subscribe(data => {
      this.inProgressAlgorithms = true;
      if (data && data['PredictedFields'] != "") {
        this.predictedFieldsInformation = data['PredictedFields'];
        this.predFields = data['PredictedFields'];
        this.predictedFieldsInformation.forEach((predictedField, index) => {
          this.algorithmsInformation.push(predictedField['Algorithms']);
        });
      } else {
        this.inProgressAlgorithms = false;
      }
    })
    this.httpClient.get('/api/algorithms/' + this.customerId + "/" + this.datasetID + "/Tuning").subscribe(data => {
      if (data && data['PredictedFields'] != "") {
        this.tunedAlgorithms = true;
        this.tunedPredictedFieldsInformation = data['PredictedFields'];
        this.tunedPredictedFieldsInformation.forEach((tunedPredictedField, index) => {
          this.tunedAlgorithmsInformation.push(tunedPredictedField['Algorithms']);
        });
      } else {
        this.tunedAlgorithms = false;
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
  public onTune() {
    let temp = [];
    this.numberFormat = /^[0-9]{1,3}$/;
    let status = 0;
    let traininMode = this.LRTrainingMode;
    let algorithms = ["RandomForestClassifier", "SVC", "MultinomialNB", "LogisticRegression", "XGBClassifier"]
    var BreakException = {}
    try {
      algorithms.forEach((algorithm, index) => {
        this.status = 0;
        let temp2 = {};
        temp2["Parameters"] = []
        if (index == 0) {
          temp2["AlgorithmName"] = algorithm;
          this.defaultRFCParameters.forEach((algo, i) => {
            if (algo['ParameterName'] == 'max_depth') {
              if (!this.numberFormat.test(algo['Value'])) {
                this.status = 1;
                alert('Enter valid max depth  for RFC Algorithm');
                throw BreakException;
              }
            }
            if (algo['ParameterName'] == 'n_estimators') {
              if (this.RFCTrainingMode == "Single") {
                if (!this.numberFormat.test(algo['Value'])) {
                  this.status = 1;
                  alert('Enter valid number of trees for RFC Algorithm');
                  throw BreakException;
                }
                temp2["ParameterType"] = this.RFCTrainingMode;
                temp2["Parameters"] = this.defaultRFCParameters;
              }
            }
          });
          if (this.RFCTrainingMode == "Multiple") {
            let temp3 = {};
            temp3["ParameterName"] = "n_estimators";
            if (!this.numberFormat.test(this.minRFC)) {
              this.status = 1;
              alert('Enter valid min number for RFC Algorithm');
              throw BreakException;
            }
            if (!this.numberFormat.test(this.maxRFC)) {
              this.status = 1;
              alert('Enter valid max number for RFC Algorithm');
              throw BreakException;
            }
            if (!this.numberFormat.test(this.pointsRFC)) {
              this.status = 1;
              alert('Enter valid points for RFC Algorithm');
              throw BreakException;
            }
            temp3["Value"] = [this.minRFC, this.maxRFC, this.pointsRFC];
            temp2["Parameters"].push(temp3);
            temp3 = {};
            temp3["ParameterName"] = "criterion";
            this.defaultRFCParameters.forEach(parameter => {
              if (parameter['ParameterName'] == 'criterion') {
                temp3["Value"] = parameter['Value'];
              }
            });
            temp2["Parameters"].push(temp3);
            temp3 = {};
            temp3["ParameterName"] = "max_depth";
            this.defaultRFCParameters.forEach(parameter => {
              if (parameter['ParameterName'] == 'max_depth') {
                temp3["Value"] = parameter['Value'];
              }
            });
            temp2["Parameters"].push(temp3);
            temp2["ParameterType"] = this.RFCTrainingMode;
          }
          temp.push(temp2);
        }
        if (index == 1) {
          temp2["AlgorithmName"] = algorithm;
          this.defaultSVCParameters.forEach((algo, i) => {
            if (i == 0) {
              if (temp2["ParameterType"] == "Single") {
                if (!this.numberFormat.test(algo['Value'])) {
                  this.status = 1;
                  alert('Enter valid  number for SVC Algorithm');
                  throw BreakException;
                }
                temp2["Parameters"] = this.defaultSVCParameters;
                temp2["ParameterType"] = this.SVCTrainingMode;
              }
            }
          });
          if (temp2["ParameterType"] == "Multiple") {
            let temp3 = {};
            temp3["ParameterName"] = "C";
            if (!this.numberFormat.test(this.minSVC)) {
              this.status = 1;
              alert('Enter valid  min number for SVC Algorithm');
              throw BreakException;
            }
            if (!this.numberFormat.test(this.maxSVC)) {
              this.status = 1;
              alert('Enter valid  max number for SVC Algorithm');
              throw BreakException;
            }
            if (!this.numberFormat.test(this.pointsSVC)) {
              this.status = 1;
              alert('Enter valid  points for SVC Algorithm');
              throw BreakException;
            }
            temp3["Value"] = [this.minSVC, this.maxSVC, this.pointsSVC];
            temp2["Parameters"].push(temp3);
            temp3 = {};
            temp3["ParameterName"] = "kernel";
            this.defaultSVCParameters.forEach(parameter => {
              if (parameter['ParameterName'] == 'kernel') {
                temp3["Value"] = parameter['Value'];
              }
            });
            temp2["Parameters"].push(temp3);
          }
          temp.push(temp2);
        }
        if (index == 2) {
          temp2["AlgorithmName"] = algorithm;
          this.defaultNBParameters.forEach((algo, i) => {
            if (i == 0) {
              temp2["ParameterType"] = this.NBTrainingMode;
              if (temp2["ParameterType"] == "Single") {
                if (!this.numberFormat.test(algo['Value'])) {
                  this.status = 1;
                  alert('Enter valid number For NB Algorithm');
                  throw BreakException;
                }
                temp2["Parameters"] = this.defaultNBParameters;
              }
            }
          });
          if (temp2["ParameterType"] == "Multiple") {
            let temp3 = {};
            temp3["ParameterName"] = "alpha";
            if (!this.numberFormat.test(this.minNB)) {
              this.status = 1;
              alert('Enter valid min number For NB Algorithm');
              throw BreakException;
            }
            if (!this.numberFormat.test(this.maxNB)) {
              this.status = 1;
              alert('Enter valid max number For NB Algorithm');
              throw BreakException;
            }
            if (!this.numberFormat.test(this.pointsNB)) {
              this.status = 1;
              alert('Enter valid points For NB Algorithm');
              throw BreakException;
            }
            temp3["Value"] = [this.minNB, this.maxNB, this.pointsNB];
            temp2["Parameters"].push(temp3);
          }
          temp.push(temp2);
        }
        if (index == 3) {
          temp2["AlgorithmName"] = algorithm;
          this.defaultLRParameters.forEach((algo, i) => {
            if (i == 0) {
              temp2["ParameterType"] = this.LRTrainingMode;
              if (temp2["ParameterType"] == "Single") {
                if (!this.numberFormat.test(algo['Value'])) {
                  status = 1;
                  alert('Enter valid number for LR Algorithm');
                  throw BreakException;
                }
                temp2["Parameters"] = this.defaultLRParameters;
              }
            }
          });
          if (temp2["ParameterType"] == "Multiple") {
            let temp3 = {};
            temp3["ParameterName"] = "C";
            if (!this.numberFormat.test(this.minLR)) {
              this.status = 1;
              alert('Enter valid min number for LR Algorithm');
              throw BreakException;
            }
            if (!this.numberFormat.test(this.maxLR)) {
              this.status = 1;
              alert('Enter valid max number for LR Algorithm');
              throw BreakException;
            }
            if (!this.numberFormat.test(this.pointsLR)) {
              this.status = 1;
              alert('Enter valid points for LR Algorithm');
              throw BreakException;
            }
            temp3["Value"] = [this.minLR, this.maxLR, this.pointsLR];
            temp2["Parameters"].push(temp3);
          }
          temp.push(temp2);
        }
        if (index == 4) {
          temp2["AlgorithmName"] = algorithm;
          this.defaultXGBParameters.forEach((algo, i) => {
            if (i == 0) {
              temp2["ParameterType"] = this.XGBTrainingMode;
              if (temp2["ParameterType"] == "Single") {
                if (!this.numberFormat.test(algo['Value'])) {
                  this.status = 1;
                  alert('Enter valid number For XGB Algorithm');
                  throw BreakException;
                }
                temp2["Parameters"] = this.defaultXGBParameters;
              }
              console.log(algo['ParameterName'], algo['Value']);
            }
          });
          if (temp2["ParameterType"] == "Multiple") {
            let temp3 = {};
            temp3["ParameterName"] = "n_estimators";
            if (!this.numberFormat.test(this.minXGB)) {
              this.status = 1;
              alert('Enter valid min number For XGB Algorithm');
              throw BreakException;
            }
            if (!this.numberFormat.test(this.maxXGB)) {
              this.status = 1;
              alert('Enter valid max number For XGB Algorithm');
              throw BreakException;
            }
            if (!this.numberFormat.test(this.pointsXGB)) {
              this.status = 1;
              alert('Enter valid points For XGB Algorithm');
              throw BreakException;
            }
            temp3["Value"] = [this.minXGB, this.maxXGB, this.pointsXGB];
            temp2["Parameters"].push(temp3);
            temp3 = {};
            temp3["ParameterName"] = "objective";
            this.defaultXGBParameters.forEach(parameter => {
              if (parameter['ParameterName'] == 'objective') {
                temp3["Value"] = parameter['Value'];
              }
            });
            temp2["Parameters"].push(temp3);
          }
          temp.push(temp2);
        }
      })
    } catch (e) {
      this.status = 1;
    }
    let data = {};
    data['Status'] = "Tune";
    data['Algorithms'] = temp;
    if (this.status == 0) {
      this.tuneLoading = true;
      this.httpClient.post('/api/train/' + this.customerId + "/" + this.datasetID, data).subscribe(data => {
        this.tuneLoading = false;
        this.tunedAlgorithms = false;
        this.tunedPredictedFieldsInformation = [];
        this.tunedAlgorithmsInformation = [];
        this.httpClient.get('/api/algorithms/' + this.customerId + "/" + this.datasetID + "/Tuning").subscribe(data => {
          if (data && data['PredictedFields'] != "") {
            this.tunedAlgorithms = true;
            this.tunedPredictedFieldsInformation = data['PredictedFields'];
            this.tunedPredictedFieldsInformation.forEach((tunedPredictedField, index) => {
              this.tunedAlgorithmsInformation.push(tunedPredictedField['Algorithms']);
            });
          } else {
            this.tunedAlgorithms = false;
          }
        });
      });
    }
  }
  openModal() {
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
  openVideoPopup() {
    const modalRef = this.modalService.open(TuningOptionComponent, { ariaLabelledBy: 'modal-basic-title', size: 'lg' });
    let dataPassToChild: any = {};
    if (this.predictedFieldsInformation != null) {
      modalRef.componentInstance.Summaries.push(this.predFields[0].Name);
    }
    dataPassToChild['predictedfield'] = this.predFields[0].Name;
    dataPassToChild['dataSetID'] = this.predFields[0].Name;
    dataPassToChild['customerId'] = this.predFields[0].Name;
    (<TuningOptionComponent>modalRef.componentInstance).dataToTakeAsInput = dataPassToChild;
  }
  step = -1;
  setStep(index: number) {
    this.step = index;
  }
  nextStep() {
    this.step++;
  }
  prevStep() {
    this.step--;
  }
  openCRModel(predictedFileldName: string, algorithmName: string, trainingStatus: string) {
    if (predictedFileldName && algorithmName) {
      this.httpClient.get('/api/getClassificationReport/' + this.customerId + '/' + this.datasetID + '/' + predictedFileldName + '/' + algorithmName + '/' + trainingStatus)
        .subscribe(classificationReport => {
          if (!classificationReport['failure']) {
            const modalRef = this.modalService.open(PopupModelComponent, { ariaLabelledBy: 'modal-basic-title' });
            modalRef.componentInstance.algorithmsInformation = classificationReport;
          } else {
            alert(classificationReport['failure']);
          }
        });
    } else {
      alert("some values are missing. Can't perform this operation");
    }
  }
}
