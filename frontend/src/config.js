// No login system yet, so the app is single-user for now.
// Every place that needs "the current user" imports CURRENT_USERNAME from here —
// change it in this ONE file (or wire it up to real auth later) and the whole
// app (posting, profile page, etc.) follows.
export const CURRENT_USERNAME = 'mahimashree';