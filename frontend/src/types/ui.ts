export type FilterEligibility = 'ALL' | 'ELIGIBLE' | 'POSSIBLY_ELIGIBLE';

export type SortOrder = 'DEFAULT' | 'SCORE_DESC' | 'TITLE_ASC';

export interface FilterState {
  eligibility: FilterEligibility;
  sort: SortOrder;
  minScore: number;
}
