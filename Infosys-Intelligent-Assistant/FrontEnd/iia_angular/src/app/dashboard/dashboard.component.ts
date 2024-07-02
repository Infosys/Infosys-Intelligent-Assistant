/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import * as Chartist from 'chartist';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { DatePipe } from '@angular/common'
import { now, type } from 'jquery';
import { Chart, registerables } from 'chart.js';
import { ChartOptions, ChartType, ChartDataset } from 'chart.js';
import { animate, state, style, transition, trigger } from '@angular/animations';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
declare var $;
export interface DashboardElement {
  Summary: string;
  Count: number;
}
@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  @ViewChild('pdfTable') pdfTable: ElementRef;
  dataSource: any;
  columnsToDisplay = ['Summary', 'Count'];
  expandedElement: DashboardElement | null;
  public myLineChart: Chart
  public myLineChart2: Chart
  public barChartOptions: ChartOptions = {
    responsive: true,
  };
  public barChartType: ChartType = 'bar';
  public barChartLegend = true;
  public barChartPlugins = [];
  public barChartData: ChartDataset[] = [
    { data: [65, 59, 80, 81, 56, 55, 40], label: 'Series A', stack: 'a' },
    { data: [28, 48, 40, 19, 86, 27, 90], label: 'Series B', stack: 'a' }
  ];
  openIncidentCount: number;
  closedIncidentCount: number;
  predicted_tickets: number = 12;
  ticketsfetched: number = 10;
  manuallyapprovedtickets: number = 0;
  autoapprovedtickets: number = 0;
  correctPredicted: number = 0;
  incorrectPredicted: number = 0;
  approvedtickets: number = 20;
  predictionaccuraccy: number = 0.8;
  teams: any = [];
  customerId: number = 1;
  disable: boolean;
  selectedDate: any;
  date: Date;
  selectedDate1: any;
  datasetID: number = 1;
  ID: number = 1;
  approved: number;
  assignment_group: any;
  assignment_group_count: any;
  closedtickets: number;
  assignee: any;
  assignee_count: any;
  assignee_names: any;
  assignee_name: any;
  assignee_ticket_count: number;
  dropdown: string = "Select All";
  name: any;
  listOfNames: any;
  assigneeTicket: any;
  selectedOption: string = "Select All";
  assignment_groups: any;
  assignmentGroups: any;
  countArray: any;
  countOfTicket: any;
  assignment_group1: any;
  assignment_grp_count1: any;
  end_date: string;
  from_date: string;
  default_start_date: any = Date.now
  abc: Object;
  teams1: any = []
  selected_team: string;
  emailCount: number = 0;
  click: boolean = false;
  constructor(private httpClient: HttpClient, private router: Router, public datepipe: DatePipe) {
  }
  startAnimationForLineChart(chart) {
    let seq: any, delays: any, durations: any;
    seq = 0;
    delays = 80;
    durations = 500;
    chart.on('draw', function (data) {
      if (data.type === 'line' || data.type === 'area') {
        data.element.animate({
          d: {
            begin: 600,
            dur: 700,
            from: data.path.clone().scale(1, 0).translate(0, data.chartRect.height()).stringify(),
            to: data.path.clone().stringify(),
            easing: Chartist.Svg.Easing.easeOutQuint
          }
        });
      } else if (data.type === 'point') {
        seq++;
        data.element.animate({
          opacity: {
            begin: seq * delays,
            dur: durations,
            from: 0,
            to: 1,
            easing: 'ease'
          }
        });
      }
    });
    seq = 0;
  };
  startAnimationForBarChart(chart) {
    let seq2: any, delays2: any, durations2: any;
    seq2 = 0;
    delays2 = 80;
    durations2 = 500;
    chart.on('draw', function (data) {
      if (data.type === 'bar') {
        seq2++;
        data.element.animate({
          opacity: {
            begin: seq2 * delays2,
            dur: durations2,
            from: 0,
            to: 1,
            easing: 'ease'
          }
        });
      }
    });
    seq2 = 0;
  };
  ngOnInit() {
    this.httpClient.get('/api/getTeams/' + this.customerId).subscribe(data => {
      if (data['Teams'].length > 0) {
        this.teams = data['Teams'];
        this.selected_team = this.teams[0];
        this.customerId = 1;
        this.datasetID = 1;
        this.end_date = this.datepipe.transform(new Date(), 'yyyy-MM-dd');
        this.from_date = this.datepipe.transform(Date.now() - 7 * 24 * 60 * 60 * 1000, 'yyyy-MM-dd')
        this.getDashboardSummaryData();
        this.getApprovedIncidentCount();
        this.getpredictedtickets();
        this.getticketsfetched();
        this.getOpenIncidentCount();
        this.getclosedincidents();
        this.getpredictionaccuraccy();
        this.getTeams(this.customerId);
        this.getApprovedTickets();
        this.getDashboardSummaryData();
        this.ID = 1;
        this.assigneeCount();
        this.getUsers();
        this.getAssignmentGroup();
        this.stacked_default1();
        this.getTicketsGroup();
        this.getEmailCount()
      } else {
        console.log('No Dataset found!. Create Dataset to proceed with uploading of assignment details');
      }
    }, err => {
      console.log(err);
      throw '';
    });
    /* ----------==========     Daily Incidents Chart initialization For Documentation    ==========---------- */
    const dataDailyIncidentsChart: any = {
      labels: ['M', 'T', 'W', 'T', 'F', 'S', 'S'],
      series: [
        [5, 10, 10, 20, 10, 10, 10],
        [33, 67, 47, 52, 63, 66, 104],
      ]
    };
    const optionsDailyIncidentsChart: any = {
      lineSmooth: Chartist.Interpolation.cardinal({
        tension: 0
      }),
      low: 0,
      high: 120, // recommend you to set the high sa the biggest value + something for a better look
      chartPadding: { top: 0, right: 0, bottom: 0, left: 0 },
    }
    var dailyIncidentsChart = new Chartist.Line('#dailyIncidentsChart', dataDailyIncidentsChart, optionsDailyIncidentsChart);
    this.startAnimationForLineChart(dailyIncidentsChart);
    /* ----------==========     Completed Tasks Chart initialization    ==========---------- */
    const dataCompletedTasksChart: any = {
      labels: ['12p', '3p', '6p', '9p', '12p', '3a', '6a', '9a'],
      series: [
        [230, 750, 450, 300, 280, 240, 200, 190]
      ]
    };
    const optionsCompletedTasksChart: any = {
      lineSmooth: Chartist.Interpolation.cardinal({
        tension: 0
      }),
      low: 0,
      high: 1000, // recommend you to set the high sa the biggest value + something for a better look
      chartPadding: { top: 0, right: 0, bottom: 0, left: 0 }
    }
    var completedTasksChart = new Chartist.Line('#completedTasksChart', dataCompletedTasksChart, optionsCompletedTasksChart);
    // start animation for the Completed Tasks Chart - Line Chart
    this.startAnimationForLineChart(completedTasksChart);
    /* ----------==========     Emails Subscription Chart initialization    ==========---------- */
    var datawebsiteViewsChart = {
      labels: ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'],
      series: [
        [542, 443, 320, 780, 553, 453, 326, 434, 568, 610, 756, 895]
      ]
    };
    var optionswebsiteViewsChart = {
      axisX: {
        showGrid: false
      },
      low: 0,
      high: 1000,
      chartPadding: { top: 0, right: 5, bottom: 0, left: 0 }
    };
    var responsiveOptions: any[] = [
      ['screen and (max-width: 640px)', {
        seriesBarDistance: 5,
        axisX: {
          labelInterpolationFnc: function (value) {
            return value[0];
          }
        }
      }]
    ];
    var websiteViewsChart = new Chartist.Bar('#websiteViewsChart', datawebsiteViewsChart, optionswebsiteViewsChart, responsiveOptions);
    //start animation for the Emails Subscription Chart
    this.startAnimationForBarChart(websiteViewsChart);
  }
  getDate(e) {
    this.disable = false
    this.from_date = e.target.value
    if (this.from_date > this.end_date) {
      this.from_date = this.default_start_date;
      alert('From date should not be greater than Todate')
      return;
    }
  }
  getDate1(e) {
    this.disable = false
    this.end_date = e.target.value
  }
  getToday(): string {
    return new Date().toISOString().split('T')[0]
  }
  gobutton() {
    this.getApprovedTickets();
    this.getAssignmentGroup();
    this.getTicketsGroup();
    this.getOpenTicketsByAssignee();
    this.getDashboardSummaryData();
    this.getEmailCount();
  }
  getOpenIncidentCount() {
    this.httpClient.get('/api/openTickets').subscribe(data => {
      if (data) {
        this.openIncidentCount = data as number;
      }
      else {
        this.openIncidentCount = 0;
      }
    },
      err => {
        console.log(err);
        throw "";
      });
  }
  getAssignmentGroup() {
    this.httpClient.get('/api/getAssignmentGroup/' + this.from_date + "/" + this.end_date + "/" + this.selected_team).subscribe(data => {
      if (data) {
        console.log(data);
        console.log(type(data))
        this.assignmentGroups = data;
      }
      else {
        console.log("else block,data not received")
      }
    },
      err => {
        console.log(err);
        throw "";
      });
  }
  getUsers() {
    this.httpClient.get('/api/users').subscribe(data => {
      if (data) {
        this.assignee_names = data;
      }
      else {
        console.log("else block,data not received")
      }
    },
      err => {
        console.log(err);
        throw "";
      });
  }
  category(dropdownvalue: any) {
    console.log(dropdownvalue)
    //this.dropdown="Select_All";
    if (dropdownvalue == "Select All") {
      this.dropdown = "Select All";
    }
    else {
      this.dropdown = this.selectedOption;
    }
    this.getOpenTicketsByAssignee();
  }
  getOpenTicketsByAssignee() {
    this.httpClient.get('/api/getTicketsUser' + "/" + this.from_date + "/" + this.end_date + "/" + this.dropdown + "/" + this.selected_team, { responseType: 'json' }).subscribe(data => {
      if (data["response"] == "success") {
        this.assignee_name = data["keys"]
        this.assignee_ticket_count = data["values"]
        var ctx = document.getElementById("myChart");
        if (this.myLineChart) this.myLineChart.destroy();
        this.myLineChart = new Chart(ctx, {
          type: 'horizontalBar',
          data: {
            labels: this.assignee_name,
            datasets: [{
              label: "Tickets assigned to each Assignee",
              backgroundColor: "green",
              borderColor: "rgba(2,117,216,1)",
              data: this.assignee_ticket_count,
            }],
          },
          options: {
            plugins: {
              labels: {
                render: () => { }
              }
            },
            legend: {
              display: false,
            },
            scales: {
              x: {
                beginAtZero: true,
              },
              y: {
                beginAtZero: true,
              },
              xAxes: [{
                gridLines: {
                  display: false
                },
                scaleLabel: {
                  display: true,
                  labelString: 'Count Of Tickets'
                },
                ticks: {
                  min: 0,
                  stepSize: 1,
                  display: true,
                  autoSkip: false,
                },
              }],
              yAxes: [{
                gridLines: {
                  display: false
                },
                scaleLabel: {
                  display: true,
                  labelString: 'Name of Assignee'
                },
                ticks: {
                  min: 0,
                  stepSize: 1,
                  display: true,
                },
              }],
            },
            title: {
              display: true,
              text: 'Tickets Assigned to each Assignee',
              fontSize: 20,
              position: 'top',
              font: {
                size: 500,
                weight: 'bolder'
              }
            }
          }
        });
      }
      else {
        console.log("else block,data not received")
      }
    },
      err => {
        console.log(err);
        throw "";
      });
  }
  getTicketsGroup() {
    this.httpClient.get('/api/getTicketsGroup' + "/" + this.from_date + "/" + this.end_date + "/" + this.selected_team).subscribe(data => {
      if (data["response"] == "success") {
        this.assignee_name = data["keys"]
        this.assignee_ticket_count = data["values"]
        var ctx = document.getElementById("myChart2");
        if (this.myLineChart2) this.myLineChart2.destroy();
        this.myLineChart2 = new Chart(ctx, {
          type: 'horizontalBar',
          data: {
            labels: this.assignee_name,
            datasets: [{
              label: "Tickets assigned to each Assignee",
              backgroundColor: "#CDDC39",
              borderColor: "rgba(2,117,216,1)",
              data: this.assignee_ticket_count,
            }],
            // plugins:[plugin],
          },
          options: {
            plugins: {
              labels: {
                render: () => { }
              }
            },
            legend: {
              display: false,
            },
            scales: {
              x: {
                beginAtZero: true,
              },
              y: {
                beginAtZero: true,
              },
              xAxes: [{
                gridLines: {
                  display: false
                },
                scaleLabel: {
                  display: true,
                  labelString: 'Count of tickets'
                },
                ticks: {
                  min: 0,
                  stepSize: 1,
                  display: true,
                  autoSkip: false,
                },
              }],
              yAxes: [{
                gridLines: {
                  display: false
                },
                scaleLabel: {
                  display: true,
                  labelString: 'Assignment groups'
                },
                ticks: {
                  min: 0,
                  stepSize: 1,
                  display: true,
                },
              }],
            },
            title: {
              display: true,
              text: 'Tickets classification based on assignment group',
              position: 'top',
              font: {
                size: 50,
                weight: 'bolder'
              }
            }
          }
        });
      }
      else {
        alert("No data for selected assignee")
      }
    },
      err => {
        console.log(err);
        throw "";
      });
  }
  stacked_default1() {
    this.httpClient.get('/api/generateassignee/' + this.customerId, { responseType: 'json' })
      .subscribe(data => {
        if (data) {
          this.assigneeTicket = data
          let labels: any = data
          this.listOfNames = labels.map(x => x[0])
          this.assignment_groups = labels.map(x => x[1]);
          this.countOfTicket = labels.map(x => x[2]);
          this.assignment_groups.forEach(element => {
            this.countArray = [];
            this.listOfNames.forEach(element1 => {
              this.countArray.push(labels.find(x => x[0] == element1 && x[1] == element) ? labels.find(x => x[0] == element1 && x[1] == element)[2] : 0)
            }
            )
            this.barChartData.push({ data: this.countArray, label: element, stack: 'a' })
          });
        }
      },
        err => {
          console.log(err);
          throw "";
        });
  }
  getclosedincidents() {
    this.httpClient.get('/api/closed_Tickets').subscribe(data => {
      if (data) {
        this.closedtickets = data as number;
      }
      else {
        this.closedtickets = 0;
      }
    },
      err => {
        console.log(err);
        throw "";
      });
  }
  getpredictedtickets() {
    this.httpClient.get('/api/predicted_Tickets').subscribe(data => {
      if (data) {
        this.predicted_tickets = data as number;
      }
      else {
        this.predicted_tickets = 0;
      }
    },
      err => {
        console.log(err);
        throw "";
      });
  }
  getApprovedIncidentCount() {
    this.httpClient.get('/api/approvedTicketsCount').subscribe(data => {
      if (data) {
        this.approvedtickets = data as number;
      }
      else {
        this.approvedtickets = 0;
      }
    },
      err => {
        console.log(err);
        throw "";
      });
  }
  getticketsfetched() {
    this.httpClient.get('/api/getDashboardTicketsfetched').subscribe(data => {
      if (data) {
        this.ticketsfetched = data as number;
      }
      else {
        this.ticketsfetched = 0;
      }
    },
      err => {
        console.log(err);
        throw "";
      });
  }
  getManuallyApprovedIncidentCount() {
    this.httpClient.get('/api/getmanuallyapprovedtickets').subscribe(data => {
      if (data) {
        this.manuallyapprovedtickets = data as number;
      }
      else {
        this.manuallyapprovedtickets = 0;
      }
      this.getAutoApprovedIncidentCount();
    },
      err => {
        console.log(err);
        throw "";
      });
  }
  getAutoApprovedIncidentCount() {
    this.httpClient.get('/api/getautoapprovedtickets').subscribe(data => {
      if (data) {
        this.autoapprovedtickets = data as number;
      }
      else {
        this.autoapprovedtickets = 0;
      }
      this.newfunction();
    },
      err => {
        console.log(err);
        throw "";
      });
  }
  getpredictionaccuraccy() {
    this.httpClient.get('/api/getpredictionaccuraccy').subscribe(data => {
      if (data) {
        this.predictionaccuraccy = data as number;
      }
      else {
        this.predictionaccuraccy = 0;
      }
    },
      err => {
        console.log(err);
        throw "";
      });
  }
  private getTeams(custID: number) {
    this.httpClient.get('/api/getTeams/' + this.customerId).subscribe(data => {
      this.teams = data['Teams'];
    });
  }
  navigateToPredict() {
    this.router.navigate(['/predict']);
  }
  assigneeCount() {
    this.httpClient.get('/api/generateuserdetails/' + this.customerId + "/" + this.datasetID, { responseType: 'json' })
      .subscribe(data => {
        if (data) {
          this.assignee = data["keys"]
          this.assignee_count = data["values"]
        }
      },
        err => {
          console.log(err);
          throw "";
        });
  }
  handleClick() {
    this.httpClient.get('/api/getDashboardTicketsfetchedReort').subscribe(data => {
      if (data = "Success") {
      }
      else {
        this.predictionaccuraccy = 0;
      }
    },
      err => {
        console.log(err);
        throw "";
      });
  }
  stacked_default() {
    this.httpClient.get('/api/generateassignee/' + this.customerId, { responseType: 'json' })
      .subscribe(data => {
        if (data) {
          let labels: any = data
          this.listOfNames = labels.map(x => x[0])
          this.listOfNames = this.listOfNames.filter((element, i) => i === this.listOfNames.indexOf(element))
          let assignment_groups = labels.map(x => x[1]);
          assignment_groups = assignment_groups.filter((element, i) => i === assignment_groups.indexOf(element))
          assignment_groups.forEach(element => {
            let countArray = [];
            this.listOfNames.forEach(element1 => {
              countArray.push(labels.find(x => x[0] == element1 && x[1] == element) ? labels.find(x => x[0] == element1 && x[1] == element)[2] : 0)
            }
            )
            this.barChartData.push({ data: countArray, label: element, stack: 'a' })
          });
        }
      },
        err => {
          console.log(err);
          throw "";
        });
  }
  myFunction() {
    this.date = new Date();
    let latest_date = this.datepipe.transform(this.date, 'yyyy-MM-dd');
  }
  newfunction() {
    var ctx = document.getElementById("myBarChart");
    var myLineChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Auto approved', 'Manually approved'],
        datasets: [{
          label: "Tickets Approved",
          backgroundColor: [
            'orange',
            'yellow',
            'yellow',
            'green',
            'purple',
            'orange',
            'black',
            '#4e54f3',
            'brown',
            'cyan'
          ],
          borderColor: "rgba(255,255,255,0.8)",
          data: [this.autoapprovedtickets, this.manuallyapprovedtickets]
        }],
      },
      options: {
        scales: {
        },
        legend: {
          display: true,
          position: 'top',
        },
        title: {
          display: true,
          text: 'Tickets Fetched',
          position: 'bottom',
          font: {
            size: 105,
            weight: 'bolder'
          }
        },
      }
    });
    var ctx = document.getElementById("myBarChart2");
    var myLineChart2 = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Predicted Correctly', 'Predicted Incorrectly'],
        datasets: [{
          label: "Predicted Tickets",
          backgroundColor: [
            'orange',
            'yellow',
            'yellow',
            'green',
            'purple',
            'orange',
            'black',
            '#4e54f3',
            'brown',
            'cyan'
          ],
          // hoverOffset: 4,
          borderColor: "rgba(255,255,255,0.8)",
          data: [this.correctPredicted, this.incorrectPredicted]
        }],
      },
      // plugins: [plugin],
      options: {
        scales: {
        },
        legend: {
          display: true,
          position: 'top',
        },
        title: {
          display: true,
          text: 'Predicted Tickets',
          position: 'bottom',
          font: {
            size: 105,
            weight: 'bolder'
          }
        },
      }
    });
  }
  getDashboardSummaryData() {
    this.httpClient.get('/api/getDashboardSummary' + "/" + this.from_date + "/" + this.end_date + "/" + this.selected_team).subscribe(data => {
      this.dataSource = data;
    })
  }
  async downloadPDF() {
    var data = document.getElementById('pdfTable');
    $('pdfOpenHide').attr('hidden', true);
    // To disable the scroll
    await html2canvas(data, { scrollY: -window.scrollY, scale: 3 })
      .then((canvas) => {
        const contentDataURL = canvas.toDataURL('image/png');
        // enabling the scroll
        $('pdfOpenHide').attr('hidden', true);
        let pdf = new jsPDF('l', 'mm', 'a4'); // A4 size page of PDF
        let imgWidth = 250;
        let pageHeight = pdf.internal.pageSize.getHeight();
        let imgHeight = (canvas.height * imgWidth) / canvas.width;
        let heightLeft = imgHeight;
        let position = 0;
        pdf.addImage(contentDataURL, 'PNG', 0, position, imgWidth, imgHeight);
        heightLeft -= pageHeight;
        while (heightLeft >= 0) {
          position = heightLeft - imgHeight;
          pdf.addPage();
          pdf.addImage(contentDataURL, 'PNG', 0, position, imgWidth, imgHeight);
          heightLeft -= pageHeight;
        }
        return pdf;
      })
      .then((pdf) => {
        pdf.save('dashboardSummary.pdf');
      });
  }
  getApprovedTickets() {
    this.httpClient.get('/api/getApprovedTickets' + "/" + this.from_date + "/" + this.end_date + "/" + this.selected_team).subscribe(data => {
      this.autoapprovedtickets = data[0]['Auto Approved'];
      this.manuallyapprovedtickets = data[0]['Manual Approved']
    })
    this.httpClient.get('/api/getCorrectIncorrectPrediction' + "/" + this.from_date + "/" + this.end_date + "/" + this.selected_team).subscribe(data1 => {
      //  this.dataSource = data;
      this.correctPredicted = data1[0]['Predicted Correctly'];
      this.incorrectPredicted = data1[0]['Predicted Incorrectly']
      this.newfunction();
    })
  }
  getEmailCount() {
    this.httpClient.get('/api/getEmailCreatedTickets/' + this.from_date + "/" + this.end_date + "/" + this.selected_team).subscribe(data => {
      this.click = true;
      this.emailCount = data[0]['Tickets Created from Email'];
    })
  }
}
