// Copyright 2025 The Oppia Authors. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS-IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/**
 * @fileoverview Model for creating and mutating instances of frontend
 * skill domain objects.
 */

import { ConceptCard } from 'domain/skill/concept-card.model';
import { Misconception } from 'domain/skill/misconception.model';
import { RubricExplanation } from 'domain/skill/rubric-explanation.model';

export interface SkillBackendDict {
  id: string;
  description: string;
  misconceptions: object[];
  rubrics: object[];
  skill_contents: object;
  language_code: string;
  version: number;
  next_misconception_id: number;
  superseding_skill_id: string | null;
  all_questions_merged: boolean | null;
  prerequisite_skill_ids: string[];
}

export class Skill {
  private _id: string;
  private _description: string;
  private _misconceptions: Misconception[];
  private _rubrics: RubricExplanation[];
  private _conceptCard: ConceptCard;
  private _languageCode: string;
  private _version: number;
  private _nextMisconceptionId: number;
  private _supersedingSkillId: string | null;
  private _allQuestionsMerged: boolean | null;
  private _prerequisiteSkillIds: string[];

  constructor(
    id: string,
    description: string,
    misconceptions: Misconception[],
    rubrics: RubricExplanation[],
    conceptCard: ConceptCard,
    languageCode: string,
    version: number,
    nextMisconceptionId: number,
    supersedingSkillId: string | null,
    allQuestionsMerged: boolean | null,
    prerequisiteSkillIds: string[]
  ) {
    this._id = id;
    this._description = description;
    this._misconceptions = misconceptions;
    this._rubrics = rubrics;
    this._conceptCard = conceptCard;
    this._languageCode = languageCode;
    this._version = version;
    this._nextMisconceptionId = nextMisconceptionId;
    this._supersedingSkillId = supersedingSkillId;
    this._allQuestionsMerged = allQuestionsMerged;
    this._prerequisiteSkillIds = prerequisiteSkillIds;
  }

  getId(): string {
    return this._id;
  }

  getDescription(): string {
    return this._description;
  }

  setDescription(description: string): void {
    this._description = description;
  }

  getMisconceptions(): Misconception[] {
    return this._misconceptions.slice();
  }

  getRubrics(): RubricExplanation[] {
    return this._rubrics.slice();
  }

  getConceptCard(): ConceptCard {
    return this._conceptCard;
  }

  getLanguageCode(): string {
    return this._languageCode;
  }

  getVersion(): number {
    return this._version;
  }

  getNextMisconceptionId(): number {
    return this._nextMisconceptionId;
  }

  getSupersedingSkillId(): string | null {
    return this._supersedingSkillId;
  }

  getAllQuestionsMerged(): boolean | null {
    return this._allQuestionsMerged;
  }

  getPrerequisiteSkillIds(): string[] {
    return this._prerequisiteSkillIds.slice();
  }

  static createFromBackendDict(skillBackendDict: SkillBackendDict): Skill {
    return new Skill(
      skillBackendDict.id,
      skillBackendDict.description,
      [], // misconceptions - would need proper implementation
      [], // rubrics - would need proper implementation
      ConceptCard.createFromBackendDict(skillBackendDict.skill_contents),
      skillBackendDict.language_code,
      skillBackendDict.version,
      skillBackendDict.next_misconception_id,
      skillBackendDict.superseding_skill_id,
      skillBackendDict.all_questions_merged,
      skillBackendDict.prerequisite_skill_ids
    );
  }
}