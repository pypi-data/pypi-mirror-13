from healthvaultlib.itemtypes.heartrate import HeartRate
from healthvaultlib.itemtypes.allergy import Allergy
from healthvaultlib.itemtypes.questionanswer import QuestionAnswer
from healthvaultlib.itemtypes.bloodpressure import BloodPressure
from healthvaultlib.itemtypes.comment import Comment
from healthvaultlib.itemtypes.geneticsnpresult import GeneticSnpResult
from healthvaultlib.itemtypes.educationmydatafile import EducationMydataFile
from healthvaultlib.itemtypes.familyhistorycondition import FamilyHistoryCondition
from healthvaultlib.itemtypes.bodydimension import BodyDimension
from healthvaultlib.itemtypes.cardiacprofile import CardiacProfile
from healthvaultlib.itemtypes.condition import Condition
from healthvaultlib.itemtypes.dailydietaryintake import DailyDietaryIntake
from healthvaultlib.itemtypes.weblink import WebLink
from healthvaultlib.itemtypes.papsession import PapSession
from healthvaultlib.itemtypes.peakflow import PeakFlow
from healthvaultlib.itemtypes.contact import Contact
from healthvaultlib.itemtypes.healthjournalentry import HealthJournalEntry
from healthvaultlib.itemtypes.cholesterol import Cholesterol
from healthvaultlib.itemtypes.procedure import Procedure
from healthvaultlib.itemtypes.continuityofcarerecord import ContinuityOfCareRecord
from healthvaultlib.itemtypes.labresults import LabResults
from healthvaultlib.itemtypes.applicationdatareference import ApplicationDataReference
from healthvaultlib.itemtypes.personalcontactinformation import PersonalContactInformation
from healthvaultlib.itemtypes.healthassessment import HealthAssessment
from healthvaultlib.itemtypes.clinicaldocumentarchitecture import ClinicalDocumentArchitecture
from healthvaultlib.itemtypes.appspecificinformation import AppspecificInformation
from healthvaultlib.itemtypes.hba1c import Hba1c
from healthvaultlib.itemtypes.sleepjournalentry import SleepJournalEntry
from healthvaultlib.itemtypes.microbiologylabtestresult import MicrobiologyLabTestResult
from healthvaultlib.itemtypes.familyhistoryperson import FamilyHistoryPerson
from healthvaultlib.itemtypes.menstruation import Menstruation
from healthvaultlib.itemtypes.vitalsigns import VitalSigns
from healthvaultlib.itemtypes.healthgoal import HealthGoal
from healthvaultlib.itemtypes.dischargesummary import DischargeSummary
from healthvaultlib.itemtypes.medicalimagestudy import MedicalImageStudy
from healthvaultlib.itemtypes.bloodglucose import BloodGlucose
from healthvaultlib.itemtypes.careplan import CarePlan
from healthvaultlib.itemtypes.insulininjectionusage import InsulinInjectionUsage
from healthvaultlib.itemtypes.mealdefinition import MealDefinition
from healthvaultlib.itemtypes.file import File
from healthvaultlib.itemtypes.exercisesamples import ExerciseSamples
from healthvaultlib.itemtypes.continuityofcaredocument import ContinuityOfCareDocument
from healthvaultlib.itemtypes.sleepsession import SleepSession
from healthvaultlib.itemtypes.asthmainhaler import AsthmaInhaler
from healthvaultlib.itemtypes.medicalannotation import MedicalAnnotation
from healthvaultlib.itemtypes.bodycomposition import BodyComposition
from healthvaultlib.itemtypes.weight import Weight
from healthvaultlib.itemtypes.status import Status
from healthvaultlib.itemtypes.diabeticprofile import DiabeticProfile
from healthvaultlib.itemtypes.respiratoryprofile import RespiratoryProfile
from healthvaultlib.itemtypes.fooddrink import FoodDrink
from healthvaultlib.itemtypes.aerobicprofile import AerobicProfile
from healthvaultlib.itemtypes.weightgoal import WeightGoal
from healthvaultlib.itemtypes.asthmainhalerusage import AsthmaInhalerUsage
from healthvaultlib.itemtypes.emotionalstate import EmotionalState
from healthvaultlib.itemtypes.familyhistory import FamilyHistory
from healthvaultlib.itemtypes.calorieguideline import CalorieGuideline
from healthvaultlib.itemtypes.weeklyaerobicexercisegoal import WeeklyAerobicExerciseGoal
from healthvaultlib.itemtypes.medication import Medication
from healthvaultlib.itemtypes.advancedirective import AdvanceDirective
from healthvaultlib.itemtypes.insulininjection import InsulinInjection
from healthvaultlib.itemtypes.allergicepisode import AllergicEpisode
from healthvaultlib.itemtypes.encounter import Encounter
from healthvaultlib.itemtypes.personalpicture import PersonalPicture
from healthvaultlib.itemtypes.exercise import Exercise
from healthvaultlib.itemtypes.healthcareproxy import HealthcareProxy
from healthvaultlib.itemtypes.bloodoxygensaturation import BloodOxygenSaturation
from healthvaultlib.itemtypes.immunization import Immunization
from healthvaultlib.itemtypes.message import Message
from healthvaultlib.itemtypes.personaldemographicinformation import PersonalDemographicInformation
from healthvaultlib.itemtypes.height import Height
from healthvaultlib.itemtypes.pregnancy import Pregnancy
from healthvaultlib.itemtypes.medicalproblem import MedicalProblem
from healthvaultlib.itemtypes.medicaldevice import MedicalDevice
from healthvaultlib.itemtypes.radiologyresult import RadiologyResult
from healthvaultlib.itemtypes.concern import Concern
from healthvaultlib.itemtypes.groupmembership import GroupMembership
from healthvaultlib.itemtypes.groupmembershipactivity import GroupMembershipActivity
from healthvaultlib.itemtypes.medicationfill import MedicationFill
from healthvaultlib.itemtypes.dailymedicationusage import DailyMedicationUsage
from healthvaultlib.itemtypes.insuranceplan import InsurancePlan
from healthvaultlib.itemtypes.educationsifstudentacademicrecord import EducationSifStudentAcademicRecord
from healthvaultlib.itemtypes.educationdocument import EducationDocument
from healthvaultlib.itemtypes.appointment import Appointment
from healthvaultlib.itemtypes.passwordprotectedpackage import PasswordprotectedPackage
from healthvaultlib.itemtypes.lifegoal import LifeGoal
from healthvaultlib.itemtypes.defibrillatorepisode import DefibrillatorEpisode
from healthvaultlib.itemtypes.explanationofbenefits import ExplanationOfBenefits
from healthvaultlib.itemtypes.healthevent import HealthEvent
from healthvaultlib.itemtypes.contraindication import Contraindication
from healthvaultlib.itemtypes.basicdemographicinformation import BasicDemographicInformation



class ItemTypeResolver():
    itemtype_dict = {}

    def __init__(self):
        self.itemtype_dict['b81eb4a6-6eac-4292-ae93-3872d6870994'] = HeartRate
        self.itemtype_dict['52bf9104-2c5e-4f1f-a66d-552ebcc53df7'] = Allergy
        self.itemtype_dict['55d33791-58de-4cae-8c78-819e12ba5059'] = QuestionAnswer
        self.itemtype_dict['ca3c57f4-f4c1-4e15-be67-0a3caf5414ed'] = BloodPressure
        self.itemtype_dict['9f4e0fcd-10d7-416d-855a-90514ce2016b'] = Comment
        self.itemtype_dict['9d006053-116c-43cc-9554-e0cda43558cb'] = GeneticSnpResult
        self.itemtype_dict['0aa6a4c7-cef5-46ea-970e-206c8402dccb'] = EducationMydataFile
        self.itemtype_dict['6705549b-0e3d-474e-bfa7-8197ddd6786a'] = FamilyHistoryCondition
        self.itemtype_dict['dd710b31-2b6f-45bd-9552-253562b9a7c1'] = BodyDimension
        self.itemtype_dict['adaf49ad-8e10-49f8-9783-174819e97051'] = CardiacProfile
        self.itemtype_dict['7ea7a1f9-880b-4bd4-b593-f5660f20eda8'] = Condition
        self.itemtype_dict['9c29c6b9-f40e-44ff-b24e-fba6f3074638'] = DailyDietaryIntake
        self.itemtype_dict['d4b48e6b-50fa-4ba8-ac73-7d64a68dc328'] = WebLink
        self.itemtype_dict['9085cad9-e866-4564-8a91-7ad8685d204d'] = PapSession
        self.itemtype_dict['5d8419af-90f0-4875-a370-0f881c18f6b3'] = PeakFlow
        self.itemtype_dict['25c94a9f-9d3d-4576-96dc-6791178a8143'] = Contact
        self.itemtype_dict['21d75546-8717-4deb-8b17-a57f48917790'] = HealthJournalEntry
        self.itemtype_dict['98f76958-e34f-459b-a760-83c1699add38'] = Cholesterol
        self.itemtype_dict['df4db479-a1ba-42a2-8714-2b083b88150f'] = Procedure
        self.itemtype_dict['1e1ccbfc-a55d-4d91-8940-fa2fbf73c195'] = ContinuityOfCareRecord
        self.itemtype_dict['5800eab5-a8c2-482a-a4d6-f1db25ae08c3'] = LabResults
        self.itemtype_dict['9ad2a94f-c6a4-4d78-8b50-75b65be0e250'] = ApplicationDataReference
        self.itemtype_dict['162dd12d-9859-4a66-b75f-96760d67072b'] = PersonalContactInformation
        self.itemtype_dict['58fd8ac4-6c47-41a3-94b2-478401f0e26c'] = HealthAssessment
        self.itemtype_dict['1ed1cba6-9530-44a3-b7b5-e8219690ebcf'] = ClinicalDocumentArchitecture
        self.itemtype_dict['a5033c9d-08cf-4204-9bd3-cb412ce39fc0'] = AppspecificInformation
        self.itemtype_dict['62160199-b80f-4905-a55a-ac4ba825ceae'] = Hba1c
        self.itemtype_dict['031f5706-7f1a-11db-ad56-7bd355d89593'] = SleepJournalEntry
        self.itemtype_dict['b8fcb138-f8e6-436a-a15d-e3a2d6916094'] = MicrobiologyLabTestResult
        self.itemtype_dict['cc23422c-4fba-4a23-b52a-c01d6cd53fdf'] = FamilyHistoryPerson
        self.itemtype_dict['caff3ff3-812f-44b1-9c9f-c1af13167705'] = Menstruation
        self.itemtype_dict['73822612-c15f-4b49-9e65-6af369e55c65'] = VitalSigns
        self.itemtype_dict['dad8bb47-9ad0-4f09-a020-0ff051d1d0f7'] = HealthGoal
        self.itemtype_dict['02ef57a2-a620-425a-8e92-a301542cca54'] = DischargeSummary
        self.itemtype_dict['cdfc0a9b-6d3b-4d16-afa8-02b86d621a8d'] = MedicalImageStudy
        self.itemtype_dict['879e7c04-4e8a-4707-9ad3-b054df467ce4'] = BloodGlucose
        self.itemtype_dict['415c95e0-0533-4d9c-ac73-91dc5031186c'] = CarePlan
        self.itemtype_dict['184166be-8adb-4d9c-8162-c403040e31ad'] = InsulinInjectionUsage
        self.itemtype_dict['074e122a-335a-4a47-a63d-00a8f3e79e60'] = MealDefinition
        self.itemtype_dict['bd0403c5-4ae2-4b0e-a8db-1888678e4528'] = File
        self.itemtype_dict['e1f92d7f-9699-4483-8223-8442874ec6d9'] = ExerciseSamples
        self.itemtype_dict['9c48a2b8-952c-4f5a-935d-f3292326bf54'] = ContinuityOfCareDocument
        self.itemtype_dict['11c52484-7f1a-11db-aeac-87d355d89593'] = SleepSession
        self.itemtype_dict['ff9ce191-2096-47d8-9300-5469a9883746'] = AsthmaInhaler
        self.itemtype_dict['7ab3e662-cc5b-4be2-bf38-78f8aad5b161'] = MedicalAnnotation
        self.itemtype_dict['18adc276-5144-4e7e-bf6c-e56d8250adf8'] = BodyComposition
        self.itemtype_dict['3d34d87e-7fc1-4153-800f-f56592cb0d17'] = Weight
        self.itemtype_dict['d33a32b2-00de-43b8-9f2a-c4c7e9f580ec'] = Status
        self.itemtype_dict['80cf4080-ad3f-4bb5-a0b5-907c22f73017'] = DiabeticProfile
        self.itemtype_dict['5fd15cb7-b717-4b1c-89e0-1dbcf7f815dd'] = RespiratoryProfile
        self.itemtype_dict['089646a6-7e25-4495-ad15-3e28d4c1a71d'] = FoodDrink
        self.itemtype_dict['7b2ea78c-4b78-4f75-a6a7-5396fe38b09a'] = AerobicProfile
        self.itemtype_dict['b7925180-d69e-48fa-ae1d-cb3748ca170e'] = WeightGoal
        self.itemtype_dict['03efe378-976a-42f8-ae1e-507c497a8c6d'] = AsthmaInhalerUsage
        self.itemtype_dict['4b7971d6-e427-427d-bf2c-2fbcf76606b3'] = EmotionalState
        self.itemtype_dict['4a04fcc8-19c1-4d59-a8c7-2031a03f21de'] = FamilyHistory
        self.itemtype_dict['d3170d30-a41b-4bde-a116-87698c8a001a'] = CalorieGuideline
        self.itemtype_dict['e4501363-fb95-4a11-bb60-da64e98048b5'] = WeeklyAerobicExerciseGoal
        self.itemtype_dict['30cafccc-047d-4288-94ef-643571f7919d'] = Medication
        self.itemtype_dict['822a5e5a-14f1-4d06-b92f-8f3f1b05218f'] = AdvanceDirective
        self.itemtype_dict['3b3c053b-b1fe-4e11-9e22-d4b480de74e8'] = InsulinInjection
        self.itemtype_dict['d65ad514-c492-4b59-bd05-f3f6cb43ceb3'] = AllergicEpisode
        self.itemtype_dict['464083cc-13de-4f3e-a189-da8e47d5651b'] = Encounter
        self.itemtype_dict['a5294488-f865-4ce3-92fa-187cd3b58930'] = PersonalPicture
        self.itemtype_dict['85a21ddb-db20-4c65-8d30-33c899ccf612'] = Exercise
        self.itemtype_dict['7ea47715-cba4-47f0-99d2-eb0a9fb4a85c'] = HealthcareProxy
        self.itemtype_dict['3a54f95f-03d8-4f62-815f-f691fc94a500'] = BloodOxygenSaturation
        self.itemtype_dict['cd3587b5-b6e1-4565-ab3b-1c3ad45eb04f'] = Immunization
        self.itemtype_dict['72dc49e1-1486-4634-b651-ef560ed051e5'] = Message
        self.itemtype_dict['92ba621e-66b3-4a01-bd73-74844aed4f5b'] = PersonalDemographicInformation
        self.itemtype_dict['40750a6a-89b2-455c-bd8d-b420a4cb500b'] = Height
        self.itemtype_dict['46d485cf-2b84-429d-9159-83152ba801f4'] = Pregnancy
        self.itemtype_dict['5e2c027e-3417-4cfc-bd10-5a6f2e91ad23'] = MedicalProblem
        self.itemtype_dict['ef9cf8d5-6c0b-4292-997f-4047240bc7be'] = MedicalDevice
        self.itemtype_dict['e4911bd3-61bf-4e10-ae78-9c574b888b8f'] = RadiologyResult
        self.itemtype_dict['aea2e8f2-11dd-4a7d-ab43-1d58764ebc19'] = Concern
        self.itemtype_dict['66ac44c7-1d60-4e95-bb5b-d21490e91057'] = GroupMembership
        self.itemtype_dict['e75fa095-31ed-4b30-b5f7-463963b5e734'] = GroupMembershipActivity
        self.itemtype_dict['167ecf6b-bb54-43f9-a473-507b334907e0'] = MedicationFill
        self.itemtype_dict['a9a76456-0357-493e-b840-598bbb9483fd'] = DailyMedicationUsage
        self.itemtype_dict['9366440c-ec81-4b89-b231-308a4c4d70ed'] = InsurancePlan
        self.itemtype_dict['c3353437-7a5e-46be-8e1a-f93dac872a68'] = EducationSifStudentAcademicRecord
        self.itemtype_dict['9df1163d-eae1-405e-8a66-8aaf19bd5fc7'] = EducationDocument
        self.itemtype_dict['4b18aeb6-5f01-444c-8c70-dbf13a2f510b'] = Appointment
        self.itemtype_dict['c9287326-bb43-4194-858c-8b60768f000f'] = PasswordprotectedPackage
        self.itemtype_dict['609319bf-35cc-40a4-b9d7-1b329679baaa'] = LifeGoal
        self.itemtype_dict['a3d38add-b7b2-4ccd-856b-9b14bbc4e075'] = DefibrillatorEpisode
        self.itemtype_dict['356fbba9-e0c9-4f4f-b0d9-4594f2490d2f'] = ExplanationOfBenefits
        self.itemtype_dict['1572af76-1653-4c39-9683-9f9ca6584ba3'] = HealthEvent
        self.itemtype_dict['046d0ad7-6d7f-4bfd-afd4-4192ca2e913d'] = Contraindication
        self.itemtype_dict['3b3e6b16-eb69-483c-8d7e-dfe116ae6092'] = BasicDemographicInformation

    def get_class(self, typeid):
        return self.itemtype_dict[typeid]
