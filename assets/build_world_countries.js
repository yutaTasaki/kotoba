// 世界の地図（v20）の国の表 assets/world_countries.json を作る。
// 使い方：node assets/build_world_countries.js <codes.json> <ja.json> <en.json> <countries-110m.json>
//   codes.json・ja.json・en.json … i18n-iso-countries 7.14.0（https://cdn.jsdelivr.net/npm/i18n-iso-countries@7.14.0/）
//   countries-110m.json            … world-atlas 2.0.2（assets に置いたもの）
// 仕様書：docs/sekai/spec/sekai_chizu_shiyou.md（1.3・1.6・付録A・付録B）
const fs = require('fs');
const [codesPath, jaPath, enPath, atlasPath] = process.argv.slice(2);
const codes = JSON.parse(fs.readFileSync(codesPath, 'utf8'));          // [[alpha2, alpha3, numeric, …], …]
const ja = JSON.parse(fs.readFileSync(jaPath, 'utf8')).countries;       // { JP: '日本' | [...] }
const en = JSON.parse(fs.readFileSync(enPath, 'utf8')).countries;       // { US: ['United States of America', 'United States', …] }
const atlas = JSON.parse(fs.readFileSync(atlasPath, 'utf8'));
const arr = (v) => (Array.isArray(v) ? v : v ? [v] : []);

// 付録A：報道の呼び方（丸ごと一致で引く）
const ALIASES = {
  USA: ['米国', '米', 'アメリカ', '合衆国', '米国政府'], CHN: ['中国'], JPN: ['日本', '日本国'], GBR: ['英国', 'イギリス'],
  RUS: ['ロシア'], IRN: ['イラン'], KOR: ['韓国'], PRK: ['北朝鮮'], TWN: ['台湾'], DEU: ['ドイツ', '独'], FRA: ['フランス', '仏'],
  ITA: ['イタリア'], CAN: ['カナダ'], MEX: ['メキシコ'], BRA: ['ブラジル'], IND: ['インド'], SAU: ['サウジアラビア', 'サウジ'],
  ARE: ['アラブ首長国連邦', 'UAE'], ISR: ['イスラエル'], TUR: ['トルコ'], EGY: ['エジプト'], QAT: ['カタール'],
  AUS: ['オーストラリア', '豪州', '豪'], IDN: ['インドネシア'], VNM: ['ベトナム'], THA: ['タイ'], SGP: ['シンガポール'], HKG: ['香港'],
  CHE: ['スイス'], NLD: ['オランダ'], BEL: ['ベルギー'], POL: ['ポーランド'], ESP: ['スペイン'], NOR: ['ノルウェー'], UKR: ['ウクライナ'],
  ARG: ['アルゼンチン'], ZAF: ['南アフリカ'], VEN: ['ベネズエラ'], IRQ: ['イラク'], PAK: ['パキスタン'], PHL: ['フィリピン'], MYS: ['マレーシア'],
};
// 1.6：いちばん大きな島の重心でも国の外に落ちる4か国は、手で位置を持つ（経度・緯度）
const ANCHORS = { ISR: [34.9, 31.4], VNM: [105.85, 21.03], HRV: [15.98, 45.81], HTI: [-72.34, 18.54] };
// 1.6：粗い版の地図に無い小さな場所は、点だけを足す
const POINTS = {
  SGP: [103.82, 1.35], HKG: [114.17, 22.32], MAC: [113.55, 22.2], CYM: [-81.25, 19.31], BMU: [-64.78, 32.3], BHR: [50.56, 26.07],
  MLT: [14.44, 35.9], JEY: [-2.13, 49.21], GGY: [-2.58, 49.45], MUS: [57.55, -20.3], LIE: [9.55, 47.16], MCO: [7.42, 43.74],
};
// 付録B：場所の無い相手の名前の決め方
const SLOTS = {
  INT: { label: '国際機関', exact: ['IMF', '国際通貨基金', '世界銀行', 'BIS', '国際決済銀行', 'WTO', '世界貿易機関', 'NATO', '北大西洋条約機構', '国連', '国際連合', 'OPEC', 'OPEC＋', 'OPEC+', 'OECD', 'G7', 'G20'], contains: [] },
  REG: { label: '地域', exact: ['EU', '欧州連合', '欧州委員会', 'ECB', '欧州中央銀行', 'ユーロ圏'], contains: ['同盟国', '加盟国', '産油国', '諸国', '各国'] },
  MKT: { label: '市場', exact: [], contains: ['市場', '買い手', '購入者'] },   // 保有者は一般名（国内）へ。回答書 sekai_chizu_m1_kaitou.md
};

const inAtlas = new Set(atlas.objects.countries.geometries.map((g) => String(g.id)));
const countries = codes.map(([a2, a3, num]) => {
  const jaNames = arr(ja[a2]);
  const enNames = arr(en[a2]);
  const names = [...new Set([...jaNames, ...(ALIASES[a3] || []), ...enNames])];
  return [a3, String(num).padStart(3, '0'), jaNames[0] || enNames[0] || a3, names];
});
const known = new Set(countries.map((c) => c[0]));
Object.keys(ALIASES).concat(Object.keys(ANCHORS), Object.keys(POINTS)).forEach((a3) => { if (!known.has(a3)) throw new Error('表に無い国コード: ' + a3); });
const out = {
  _about: '世界の地図（v20）の国の表。assets/build_world_countries.js で作る。仕様書 docs/sekai/spec/sekai_chizu_shiyou.md',
  _sources: {
    'd3-geo.min.js': 'd3-geo 3.1.1（https://cdn.jsdelivr.net/npm/d3-geo@3.1.1/dist/d3-geo.min.js）',
    'd3-array.min.js': 'd3-array 3.2.4（https://cdn.jsdelivr.net/npm/d3-array@3.2.4/dist/d3-array.min.js）',
    'topojson-client.min.js': 'topojson-client 3.1.0（https://cdn.jsdelivr.net/npm/topojson-client@3.1.0/dist/topojson-client.min.js）',
    'countries-110m.json': 'world-atlas 2.0.2（https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-110m.json）Natural Earth 1:110m',
    'この表の国名・番号': 'i18n-iso-countries 7.14.0 の codes.json・langs/ja.json・langs/en.json に、付録A の呼び名を足したもの',
  },
  countries,            // [3文字コード, 番号（世界地図の id と同じ3桁）, 日本語名, 丸ごと一致で引く名前の一覧]
  anchors: ANCHORS,
  points: POINTS,
  slots: SLOTS,
};
fs.writeFileSync(require('path').join(__dirname, 'world_countries.json'), JSON.stringify(out));
const missingInAtlas = countries.filter((c) => !inAtlas.has(c[1]) && !POINTS[c[0]]).length;
console.log('国', countries.length, '／ 地図に形がある', countries.filter((c) => inAtlas.has(c[1])).length, '／ 点で足す', Object.keys(POINTS).length, '／ 形も点も無い', missingInAtlas);
