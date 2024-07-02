/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { AdminLayoutRoutes } from './admin-layout.routing';
import { LoaderComponent } from '../../loader/loader.component';
import { DashboardComponent } from '../../dashboard/dashboard.component';
import { InputOutputComponent } from '../../training/input-output/input-output.component';
import { TrainingComponent } from '../../training/training.component';
import { AlgorithmFilterComponent } from '../../training/algorithm-filter/algorithm-filter.component';
import { AlgorithmInformationComponent } from '../../training/algorithm-information/algorithm-information.component';
import { UserPreferenceComponent } from '../../user-preference/user-preference.component';
import { ResourcePlanningComponent } from '../../resource-planning/resource-planning.component';
import { ResourceDetailsComponent } from '../../resource-planning/resource-details/resource-details.component';
import { ApplicationDetailsComponent } from '../../resource-planning/application-details/application-details.component';
import { RoasterDetailsComponent } from '../../resource-planning/roaster-details/roaster-details.component';
import { ShiftDetailsComponent } from '../../resource-planning/roaster-details/shift-details/shift-details.component';
import { PredictComponent } from '../../predict/predict.component';
import { TicketComponent } from '../../ticket/ticket.component';
import { RetrainingComponent } from '../../retraining/retraining.component';
import { TicketWeightageComponent } from '../../resource-planning/ticket-weightage/ticket-weightage.component'
import { AdminComponent } from '../../admin/admin.component'
import { ApplicaitonLevelSettingsComponent } from '../../admin/application-level-settings/application-level-settings.component'
import { ITSMDetialsComponent } from '../../admin/itsm-details/itsm-details.component'
import { NotificationsComponent } from '../../admin/notifications/notifications.component'
import { OtherSettingsComponent } from '../../admin/other-settings/other-settings.component'
import { TeamDetailsComponent } from '../../admin/team-details/team-details.component'
import { AngularMultiSelectModule } from 'angular2-multiselect-dropdown/angular2-multiselect-dropdown';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatTabsModule } from '@angular/material/tabs';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { ChartsModule } from 'ng2-charts';
import { Chart } from 'chart.js';
import { TagCloudModule } from 'angular-tag-cloud-module';
import { TagInputModule } from 'ngx-chips';
import { NgbModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
import { AboutPageComponent } from '../../about-page/about-page.component';
import { AddUserComponent } from '../../admin/add-user/add-user.component';
// import {FlexModule} from '@angular/flex-layout';
import { ScriptsPopupComponent } from '../../ticket/scripts-popup/scripts-popup.component'
import { LogsComponent } from '../../ticket/logs/logs.component'
import { ScriptsConfigurationComponent } from '../../admin/scripts-configuration/scripts-configuration.component'
import { MatAutocompleteSelectedEvent, MatChipInputEvent, MatAutocomplete, MatChipInput, MatAutocompleteModule } from '@angular/material';
import { MatChipsModule } from '@angular/material/chips'
import {
  MatButtonModule,
  MatInputModule,
  MatRippleModule,
  MatTooltipModule,
  MatCheckboxModule,
  MatSliderModule,
  MatSortModule,
  MatDialogModule,
  MatRadioModule
} from '@angular/material';
import { MatTableModule, MatPaginatorModule } from '@angular/material';
import { CdkTableModule } from '@angular/cdk/table';
import { ScriptManagementComponent } from '../../admin/script-management/script-management.component';
import { ScriptsMappingComponent } from '../../admin/script-mapping/script-mapping.component';
import { ScriptRunComponent } from '../../admin/script-run/script-run.component';
import { AdminUserManageComponent } from '../../admin/admin-user-manage/admin-user-manage.component';
import { ITSMUserMapComponent } from '../../admin/admin-user-manage/itsm-user-map/itsm-user-map.component';
import { TagsTrainingComponent } from '../../admin/tags-training/tags-training.component'
import { TagSettingsComponent } from '../../admin/tag-settings/tag-settings.component';
import { OtherTrainingComponent } from '../../other-training/other-training.component';
import { NERTrainingComponent } from '../../other-training/NER-training/NER-training.component';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { WorkflowComponent } from '../../admin/workflow/workflow.component';
import { PMAComponent } from '../../training/PMA/PMA.component';
import { MonthlyDetailComponent } from '../../training/PMA/monthly-details/monthly-details.component';
import { PMAAssignementComponent } from '../../training/PMA/PMA-Assignment/PMA-Assignment.component';
import { PieAnalysisComponent } from '../../training/PMA/pie-analysis/pie-analysis.component';
import { PMATagDetailsComponent } from '../../admin/pma-tag-details/pma-tag-details.component';
// import { NgMultiSelectDropDownModule } from 'ng-multiselect-dropdown'; 
import { PickListModule } from 'primeng/picklist';
import { NERConfigurationComponent } from '../../other-training/NER-configuration/NER-configuration.component';
import { knowledgeInfoComponent } from '../../other-training/knowledge-info/knowledge-info.component';
import { WeightedMovingAverageComponent } from '../../training/PMA/weighted-moving-average/weighted-moving-average.component'
import { RelatedTicketsModalComponent } from '../../ticket/related-tickets/related-tickets-modal/related-tickets-modal.component';
import { ClusteringComponent } from '../../training/PMA/clustering/clustering.component';
import { CalendarHeatmapComponent } from '../../training/PMA/calendar-heatmap/calendar-heatmap.component';
import { LineGraphComponent } from '../../training/PMA/line-graph/line-graph.component'
import { KnowledgeInfoMappingModalComponent } from '../../other-training/knowledge-info/knowledge-info-mapping-modal/knowledge-info-mapping-modal.component';
import {OneshotLearningComponent} from '../../other-training/oneshot-learning/oneshot-learning.component';
import {ChooseImageModalComponent} from '../../other-training/oneshot-learning/chooseimage-modal/chooseimage-modal.component';
import {BOTimageAnalysisComponent} from '../../other-training/BOT-imageanalysis/BOT-imageanalysis.component';
import {imageAnalysisDetailsComponent } from '../../admin/image-analysis-details/image-analysis-details.component';
import { FileuploadComponent } from '../../training/PMA/fileupload/fileupload.component';
import { MappingDetailsComponent } from "../../resource-planning/mapping-details/mapping_details.component";
import { ResourceShiftDetailsComponent } from "../../resource-planning/resource_shift_details/resource_shift_details.component";
import { RosterFileUploadComponent } from '../../resource-planning/roster-file-upload/roster-file-upload.component'
import { RPABotManagementComponent } from '../../admin/rpa-bot-management/rpa-bot-management.component';
@NgModule({
  imports: [
    CdkTableModule,
    CommonModule,
    RouterModule.forChild(AdminLayoutRoutes),
    FormsModule,
    ReactiveFormsModule,
    MatButtonModule,
    MatRippleModule,
    MatSelectModule,
    MatExpansionModule,
    MatIconModule,
    MatInputModule,
    MatTooltipModule,
    AngularMultiSelectModule,
    MatTabsModule,
    MatDatepickerModule,
    NgbModule,
    MatTabsModule,
    TagInputModule,
    TagCloudModule,
    ChartsModule,
    MatCheckboxModule,
    MatAutocompleteModule,
    MatChipsModule,
    MatSliderModule,
    MatSlideToggleModule,
    MatSortModule,
    MatPaginatorModule,
    MatTableModule,
    MatButtonToggleModule,
    MatDialogModule,
    PickListModule,
    MatRadioModule,    
    // NgMultiSelectDropDownModule
  ],
  declarations: [
    DashboardComponent,
    InputOutputComponent,
    PredictComponent,
    TicketComponent,
    AlgorithmInformationComponent,
    TrainingComponent,
    UserPreferenceComponent,
    AlgorithmFilterComponent,
    ResourcePlanningComponent,
    ResourceDetailsComponent,
    ApplicationDetailsComponent,
    RoasterDetailsComponent,
    ShiftDetailsComponent,
    LoaderComponent,
    RetrainingComponent,
    TicketWeightageComponent,
    ApplicaitonLevelSettingsComponent,
    ITSMDetialsComponent,
    NotificationsComponent,
    OtherSettingsComponent,
    TeamDetailsComponent,
    AdminComponent,
    AboutPageComponent,
    AddUserComponent,
    ScriptsConfigurationComponent,
    ScriptManagementComponent,
    ScriptsMappingComponent,
    WorkflowComponent,
    ScriptRunComponent,
    AdminUserManageComponent,
    ITSMUserMapComponent,
    TagsTrainingComponent,
    TagSettingsComponent,
    OtherTrainingComponent,
    NERTrainingComponent,
    PMAComponent,
    MonthlyDetailComponent,
    PMAAssignementComponent,
    PieAnalysisComponent,
    PMATagDetailsComponent,
    NERConfigurationComponent,
    knowledgeInfoComponent,
    WeightedMovingAverageComponent,
    RelatedTicketsModalComponent,
    OneshotLearningComponent,
    // OneShotModalComponent,
    ChooseImageModalComponent,
    // ImageOneShotModalComponent,
    BOTimageAnalysisComponent,
    imageAnalysisDetailsComponent,
    CalendarHeatmapComponent,
    LineGraphComponent,
    KnowledgeInfoMappingModalComponent,
    ClusteringComponent,
    FileuploadComponent,
    MappingDetailsComponent,    
    ResourceShiftDetailsComponent,
    RosterFileUploadComponent,
    RPABotManagementComponent,
  ],
  entryComponents: [
    RelatedTicketsModalComponent,
    KnowledgeInfoMappingModalComponent,
    ChooseImageModalComponent
  ]
})
export class AdminLayoutModule { }
