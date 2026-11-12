"""Recompute every number typed into the manuscript draft (13 November 2026) and compare with the typed value.

Run from the repository root after analyse.py. Each chk() line holds a number as it stands in the manuscript text
or tables; the script prints any that no longer agree with the data. Needs scipy.
"""
import csv, collections, pathlib, re, statistics
R = str(pathlib.Path(__file__).resolve().parents[2]) + '/'
def read(p): return list(csv.DictReader(open(R + p)))
sp = {r['species_id']: r for r in read('data/raw/species_list.csv') if r['counted'] == '1'}
grp = {s: r['group'] for s, r in sp.items()}
comb = [r for r in read('data/combined/species_state_all_sources.csv') if r['species_id'] in sp]
st = collections.defaultdict(set)
for r in comb: st[r['species_id']].add(r['state'])
by_state = collections.defaultdict(set)
for r in comb: by_state[r['state']].add(r['species_id'])
obs = read('data/aicrp/aicrp_observations.csv')
ok = bad = 0
def chk(name, got, typed):
    global ok, bad
    if got == typed: ok += 1
    else: bad += 1; print('DIFF', name, 'data:', got, 'typed:', typed)
G = collections.Counter(grp.values())
chk('checklist', len(sp), 1221)
for g, n in [('Eriophyoidea',580),('Phytoseiidae',332),('Tetranychidae',148),('Tenuipalpidae',114),('Tarsonemidae',43),('Tuckerellidae',4)]: chk(g, G[g], n)
chk('pairs', len(comb), 2468); chk('species with state', len(st), 1192); chk('no state', len(sp)-len(st), 29)
nl = collections.Counter(min(int(r['n_layers']),3) for r in comb)
chk('1 layer', nl[1], 1446); chk('2', nl[2], 859); chk('3+', nl[3], 163); chk('pct 1 layer', round(100*nl[1]/len(comb),1), 58.6)
chk('states', len(by_state), 34)
for s, n in [('West Bengal',515),('Tamil Nadu',428),('Karnataka',260),('Punjab',107),('Delhi',95),('Uttar Pradesh',94),('Assam',81),('Kerala',80),('Gujarat',59),('Andhra Pradesh',40),('Odisha',31),('Rajasthan',22),('Madhya Pradesh',22),('Maharashtra',17),('Tripura',61),('Sikkim',46)]: chk(s, len(by_state[s]), n)
T = {'West Bengal','Tamil Nadu','Karnataka'}
u = set().union(*[by_state[s] for s in T]); chk('union top3', len(u), 917); chk('pct union', round(100*len(u)/len(st),1), 76.9)
only3 = [s for s in st if st[s] <= T]; chk('only top3', len(only3), 680); chk('pct only3', round(100*len(only3)/len(st),1), 57.0)
reg = {r['region']: int(r['species']) for r in read('data/analysis/where_species_by_region.csv')}
for k, n in [('South',603),('East',539),('North',275),('North-East',206),('Islands',66),('West',65),('Central',25)]: chk('region '+k, reg[k], n)
er = [s for s in st if grp[s]=='Eriophyoidea']; chk('erio with state', len(er), 571); chk('erio only top3', sum(1 for s in er if st[s]<=T), 482); chk('pct', round(100*482/571,1), 84.4)
chk('TN erio', sum(1 for s in by_state['Tamil Nadu'] if grp[s]=='Eriophyoidea'), 311); chk('WB erio', sum(1 for s in by_state['West Bengal'] if grp[s]=='Eriophyoidea'), 253)
for s_ in ['Arunachal Pradesh','Tripura','Sikkim','Meghalaya','Andaman & Nicobar Islands']:
    chk('phyto majority '+s_, sum(1 for s in by_state[s_] if grp[s]=='Phytoseiidae')*2 > len(by_state[s_]), True)
tar = [s for s in st if grp[s]=='Tarsonemidae']; chk('tars WB', sum(1 for s in tar if 'West Bengal' in st[s]), 37); chk('tars only WB', sum(1 for s in tar if st[s]=={'West Bengal'}), 33)
one = [s for s in st if len(st[s])==1]; chk('one state', len(one), 793); chk('pct one', round(100*len(one)/len(st),1), 66.5)
c1 = collections.Counter(next(iter(st[s])) for s in one); chk('one WB', c1['West Bengal'], 266); chk('one TN', c1['Tamil Nadu'], 228); chk('one KA', c1['Karnataka'], 70); chk('one top3', 266+228+70, 564)
chk('10+', sum(1 for s in st if len(st[s])>=10), 39)
def nst(name): return len(st[next(s for s in sp if sp[s]['species']==name)])
for n_, v in [('Eutetranychus orientalis',25),('Amblyseius largoensis',23),('Tetranychus urticae',22),('Brevipalpus phoenicis',20),('Euseius alstoniae',20)]: chk(n_, nst(n_), v)
t3 = {r['group']: r for r in read('data/analysis/where_states_per_species.csv')}
for g, vals in [('Tetranychidae',(148,0,58,29,16,45)),('Tenuipalpidae',(114,0,68,24,7,15)),('Eriophyoidea',(580,9,426,98,32,15)),('Tarsonemidae',(43,0,39,2,1,1)),('Tuckerellidae',(4,0,3,1,0,0)),('Phytoseiidae',(332,20,199,51,8,54)),('All',(1221,29,793,205,64,130))]:
    r = t3[g]; chk('table3 '+g, tuple(int(r[k]) for k in ('species','no_state','one_state','two_states','three_states','four_or_more')), vals)
w = read('data/analysis/where_species_by_state.csv'); chk('25 of 31', (sum(1 for r in w[3:] if float(r['share_on_one_layer'])>0.6), len(w)-3), (25,31))
yrs = {s: int(r['year']) for s, r in sp.items() if r['year'].isdigit()}
chk('with year', len(yrs), 1171); chk('median', int(statistics.median(yrs.values())), 1982)
dec = collections.Counter(y//10*10 for y in yrs.values())
for d, n in [(1950,46),(1960,141),(1970,144),(1980,381),(1990,117),(2000,59),(2010,50),(2020,131)]: chk('decade %d'%d, dec[d], n)
chk('1980s erio', sum(1 for s,y in yrs.items() if y//10*10==1980 and grp[s]=='Eriophyoidea'), 266)
n20 = [s for s,y in yrs.items() if y>=2020]; chk('2020s phyto', sum(1 for s in n20 if grp[s]=='Phytoseiidae'), 73); chk('2020s tars', sum(1 for s in n20 if grp[s]=='Tarsonemidae'), 30); chk('2020s WB', sum(1 for s in n20 if 'West Bengal' in st[s]), 85)
for g, m in [('Tetranychidae',1966),('Tenuipalpidae',1978),('Eriophyoidea',1983),('Phytoseiidae',1983),('Tarsonemidae',2021)]:
    chk('median '+g, int(statistics.median([y for s,y in yrs.items() if grp[s]==g])), m)
al = read('config/author_aliases.csv')
def authors(a):
    for f in al:
        if f['kind']=='text': a = a.replace(f['printed'], f['read_as'])
    a = re.sub(r'[()\[\]]','',a); a = re.sub(r'\bet al\.?','',a); out=set()
    for x in re.split(r'\s*(?:&|,|\band\b)\s*', a):
        x = x.strip(' .')
        if x and not x.isdigit(): out.add(next((f['read_as'] for f in al if f['kind']=='name' and f['printed']==x), x))
    return out
A = {s: authors(r['authority']) for s, r in sp.items()}
cnt = collections.Counter(a for s in A for a in A[s])
chk('author names', len(cnt), 201)
for a, n in [('Mohanasundaram',282),('Chakrabarti',145),('Gupta',138),('Karmakar',127),('Mondal',64)]: chk(a, cnt[a], n)
top = {'Mohanasundaram','Chakrabarti','Gupta','Karmakar','Mondal'}
chk('top5 species', sum(1 for s in A if A[s]&top), 689); chk('pct', round(100*689/1221,1), 56.4)
def ag(a,g): return sum(1 for s in A if a in A[s] and grp[s]==g)
chk('Moh erio', ag('Mohanasundaram','Eriophyoidea'), 243); chk('pct', round(100*243/580,1), 41.9); chk('Chak erio', ag('Chakrabarti','Eriophyoidea'), 145); chk('pct', round(100*145/580,1), 25.0)
chk('Gupta phyto', ag('Gupta','Phytoseiidae'), 112); chk('pct', round(100*112/332,1), 33.7); chk('Karm phyto', ag('Karmakar','Phytoseiidae'), 93); chk('pct', round(100*93/332,1), 28.0); chk('Karm tars', ag('Karmakar','Tarsonemidae'), 29)
chk('1980s either', sum(1 for s,y in yrs.items() if y//10*10==1980 and A[s]&{'Mohanasundaram','Chakrabarti'}), 289); chk('2020s Karmakar', sum(1 for s in n20 if 'Karmakar' in A[s]), 98)
def home(a, h): ids=[s for s in A if a in A[s] and st[s]]; return (len(ids), sum(1 for s in ids if h in st[s]), sum(1 for s in ids if st[s]=={h}))
chk('Moh home', home('Mohanasundaram','Tamil Nadu'), (280,264,189)); chk('Chak home', home('Chakrabarti','West Bengal'), (144,121,109)); chk('Chan home', home('Channabasavanna','Karnataka')[:2], (45,38))
# hosts
PH = {'Tetranychidae','Tenuipalpidae','Eriophyoidea','Tarsonemidae','Tuckerellidae'}
gen = collections.defaultdict(set); taxa=set(); fams=set()
def add(r):
    if r['species_id'] in sp and r['host_rank_std'] in ('species','genus'):
        gen[r['species_id']].add(r['host_taxon_std'].split()[0]); taxa.add(r['host_taxon_std'])
        if r['host_family']: fams.add(r['host_family'])
for r in read('data/records/species_host.csv'):
    if r['in_india']=='1': add(r)
for r in obs: add(r)
for r in read('data/regional/regional_species_host.csv'):
    if r['host_scope']=='indian_record': add(r)
ph = [s for s in sp if grp[s] in PH]; pw = [s for s in ph if gen[s]]
chk('phytophagous', len(ph), 889); chk('with host', len(pw), 789); chk('one genus', sum(1 for s in pw if len(gen[s])==1), 581); chk('pct', round(100*581/789,1), 73.6)
for g, v in [('Eriophyoidea',(468,520,90.0)),('Tarsonemidae',(29,36,80.6)),('Tenuipalpidae',(39,98,39.8)),('Tetranychidae',(42,131,32.1))]:
    ids=[s for s in pw if grp[s]==g]; o=sum(1 for s in ids if len(gen[s])==1); chk('one genus '+g, (o,len(ids),round(100*o/len(ids),1)), v)
chk('>20', sum(1 for s in pw if len(gen[s])>20), 13)
for n_, v in [('Tetranychus urticae',118),('Eutetranychus orientalis',57),('Brevipalpus phoenicis',46),('Tetranychus macfarlanei',40),('Polyphagotarsonemus latus',39)]:
    chk('genera '+n_, len(gen[next(s for s in sp if sp[s]['species']==n_)]), v)
big = {sp[s]['species'] for s in pw if len(gen[s])>20}
chk('big list', big, {'Tetranychus urticae','Eutetranychus orientalis','Brevipalpus phoenicis','Tetranychus macfarlanei','Polyphagotarsonemus latus','Tetranychus ludeni','Tetranychus gloveri','Brevipalpus californicus','Tetranychus neocaledonicus','Tetranychus truncatus','Oligonychus indicus','Oligonychus mangiferus','Panonychus elongatus'})
hg = collections.defaultdict(set)
for s in pw:
    for g_ in gen[s]: hg[g_].add(s)
for g_, n in [('Citrus',54),('Ficus',51),('Prunus',27),('Rosa',27),('Psidium',26),('Saccharum',19),('Oryza',14),('Gossypium',13),('Cajanus',13)]: chk('host '+g_, len(hg[g_]), n)
chk('Citrus tet', sum(1 for s in hg['Citrus'] if grp[s]=='Tetranychidae'), 30); chk('Citrus ten', sum(1 for s in hg['Citrus'] if grp[s]=='Tenuipalpidae'), 18); chk('Ficus erio', sum(1 for s in hg['Ficus'] if grp[s]=='Eriophyoidea'), 28); chk('Psidium ten', sum(1 for s in hg['Psidium'] if grp[s]=='Tenuipalpidae'), 17)
ct = {r['crop_type']: int(r['phytophagous_species']) for r in read('data/analysis/hosts_by_crop_type.csv')}
for k, n in [('tree_forest',272),('fruit',202),('weed_wild',117),('ornamental',110),('medicinal_aromatic',82),('plantation_spice',72),('field_crop',70),('vegetable',51)]: chk('crop '+k, ct[k], n)
sens = read('data/analysis/hosts_sensitivity.csv'); chk('sens', (sens[1]['share_one_host_genus'], sens[2]['share_one_host_genus']), ('0.832','0.727'))
chk('host taxa', (len(taxa), len({t.split()[0] for t in taxa}), len(fams)), (1029,517,135))
chk('phyto with plant', sum(1 for s in sp if grp[s]=='Phytoseiidae' and gen[s]), 102)
# handbook comparison
bs = collections.Counter(r['book_status'] for r in comb)
chk('book classes', (bs['state_in_book'],bs['parent_or_child_state_in_book'],bs['book_gives_no_state'],bs['new_state_for_a_book_species'],bs['species_not_in_book']), (1759,11,84,466,148)); chk('not in handbook', 2468-1759, 709)
ADD = ('new_state_for_a_book_species','species_not_in_book')
chk('new state species', len({r['species_id'] for r in comb if r['book_status']==ADD[0]}), 272); nbs={r['species_id'] for r in comb if r['book_status']==ADD[1]}; chk('not in book species', len(nbs), 132)
chk('>=2022', sum(1 for s in nbs if yrs.get(s,0)>=2022), 63); chk('<2020', sum(1 for s in nbs if s in yrs and yrs[s]<2020), 53)
t4 = {r['group']: r for r in read('data/analysis/where_additions_by_group.csv')}
for g, v in [('Tetranychidae',(594,345,8,57,153,31)),('Tenuipalpidae',(239,142,1,20,61,15)),('Eriophyoidea',(795,546,0,7,188,54)),('Tarsonemidae',(62,29,1,0,10,22)),('Tuckerellidae',(5,4,0,0,1,0)),('Phytoseiidae',(773,693,1,0,53,26))]:
    r=t4[g]; chk('table4 '+g, tuple(int(r[k]) for k in ('pairs','state_in_book','parent_or_child_state_in_book','book_gives_no_state','new_state_for_a_book_species','species_not_in_book')), v)
ap = [r for r in comb if r['in_aicrp']=='1']; ab = collections.Counter(r['book_status'] for r in ap)
chk('aicrp', (len(ap), ab['state_in_book'], ab['parent_or_child_state_in_book'], ab['book_gives_no_state'], ab[ADD[0]], ab[ADD[1]]), (487,209,7,47,213,11)); chk('aicrp species with a state pair', len({r['species_id'] for r in ap}), 182); chk('aicrp species named', len({r['species_id'] for r in obs if r['species_id'] in sp}), 210)
oa = [r for r in comb if r['book_status'] in ADD and r['only_aicrp']=='1']; chk('only aicrp', (len(oa), len({r['species_id'] for r in oa})), (188,110))
so = collections.Counter(r['state'] for r in oa)
for s_, n in [('Uttar Pradesh',31),('Gujarat',28),('Assam',21),('Haryana',16),('Tamil Nadu',14),('Punjab',13),('Bihar',12),('Kerala',12)]: chk('oa '+s_, so[s_], n)
go = collections.Counter(grp[r['species_id']] for r in oa); chk('oa groups', (go['Tetranychidae'],go['Phytoseiidae'],go['Eriophyoidea'],go['Tenuipalpidae'],go['Tarsonemidae'],go['Tuckerellidae']), (50,46,43,39,9,1))
no = collections.Counter(r['valid_name'] for r in oa)
for n_, v in [('Polyphagotarsonemus latus',7),('Aceria litchii',5),('Brevipalpus californicus',5),('Aceria mangiferae',4),('Aceria granati',4),('Brevipalpus obovatus',4),('Larvacarus transitans',4)]: chk('oa '+n_, no[n_], v)
# aicrp table 2 and rows
chk('rows', len(obs), 6885); chk('species rows', sum(1 for r in obs if r['mite_rank']=='species'), 5144); chk('names', len({r['mite_name'] for r in obs if r['mite_rank']=='species'}), 387); chk('joined', sum(1 for r in obs if r['species_id']), 4664); chk('counting', sum(1 for r in obs if r['state_counts']=='1'), 6015); chk('centres', len({r['centre'] for r in obs}), 11)
t2 = {r['report']: r for r in read('data/analysis/when_aicrp_by_report.csv')}
for k, v in [('AICRP 1988',(6,510,72,91,38)),('AICRP 1989',(6,545,75,69,25)),('AICRP 1990 Group Meeting',(6,322,55,62,18)),('AICRP 1990-91',(8,1000,69,148,54)),('AICRP 1992-94',(7,347,58,115,30)),('AICRP 1996-98',(7,1109,83,169,48)),('AICRP 2020-21',(6,1978,71,132,57)),('AICRP 2021-22',(5,317,31,47,25)),('AICRP 2024-25',(7,757,80,93,56))]:
    r=t2[k]; chk('table2 '+k, tuple(int(r[x]) for x in ('centres','observation_rows','checklist_species','species_state_pairs','pairs_that_add_to_the_book')), v)
chk('rows with host', sum(1 for r in obs if r['host_as_printed']), 5103)
# table 1
sm = {r['layer']: r for r in read('data/combined/summary.csv')}
for k, v in [('chalil2024',(456,921)),('mitra2025',(175,657)),('tn2020',(277,270)),('karn2025',(49,0)),('som2025',(58,0)),('mandal2026',(230,270)),('tarswb2023',(25,0)),('gb2017',(73,163)),('mitra2018',(17,39)),('add2026',(64,37))]:
    chk('table1 '+k, (int(sm[k]['species_state_pairs']), int(sm[k]['species_host_rows'])), v)
chk('regional rows', (sum(int(sm[k]['species_state_rows']) for k in sm if sm[k]['species_state_rows']), sum(int(sm[k]['species_host_rows']) for k in sm if sm[k]['species_host_rows'])), (1432,2357))
g = read('data/records/species_state.csv'); chk('gm states', (len(g), sum(1 for r in g if r['state_basis']=='parsed'), len(g)-sum(1 for r in g if r['state_basis']=='parsed')), (2003,1966,37)); chk('gm hosts', len(read('data/records/species_host.csv')), 1588)
chk('book species', len(read('data/records/species_in_book.csv')), 1076)
# barcodes
cov = {r['species_id']: r for r in read('data/raw/coverage_by_species.csv') if r['species_id'] in sp}
bc = {s for s, r in cov.items() if int(r['n_coi'])>0}; chk('barcoded', len(bc), 137); chk('india', sum(1 for r in cov.values() if int(r['n_coi_india'])>0), 56); chk('pct', (round(100*137/1221,1), round(100*56/1221,1)), (11.2,4.6))
def cls(lo, hi): ids=[s for s in sp if lo<=len(st[s])<=hi]; return (sum(1 for s in ids if s in bc), len(ids), round(100*sum(1 for s in ids if s in bc)/len(ids),1))
chk('bc 1', cls(1,1), (34,793,4.3)); chk('bc 2-3', cls(2,3), (38,269,14.1)); chk('bc 4-9', cls(4,9), (35,91,38.5)); chk('bc 10+', cls(10,99), (27,39,69.2))
chk('medians', (statistics.median([len(st[s]) for s in bc]), statistics.median([len(st[s]) for s in sp if s not in bc]), statistics.median([len(gen[s]) for s in bc]), statistics.median([len(gen[s]) for s in sp if s not in bc])), (3,1,2,1))
from scipy import stats
u1 = stats.mannwhitneyu([len(st[s]) for s in bc], [len(st[s]) for s in sp if s not in bc], alternative='two-sided'); chk('U states', round(u1.statistic), 114936)
u2 = stats.mannwhitneyu([len(gen[s]) for s in bc], [len(gen[s]) for s in sp if s not in bc], alternative='two-sided'); chk('U hosts', round(u2.statistic), 109435)
rho = stats.spearmanr([len(st[s]) for s in sp], [1 if s in bc else 0 for s in sp]); chk('rho', round(rho.statistic,3), 0.353); chk('P<0.001', max(u1.pvalue,u2.pvalue,rho.pvalue) < 0.001, True)
chk('MP+CG+MH union < Tripura', len(by_state['Madhya Pradesh']|by_state['Chhattisgarh']|by_state['Maharashtra']) < len(by_state['Tripura']), True)
chk('Punjab gap', len(by_state['Karnataka'])-len(by_state['Punjab']) > 150, True)
chk('year conflicts', len(read('data/review/checklist_years_that_differ_between_sources.csv')), 31)
print(ok, 'agree;', bad, 'differ')
