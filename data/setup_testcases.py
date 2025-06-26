#!/usr/bin/env python3
"""
Setup comprehensive test cases for translation evaluation
"""

import os
from pathlib import Path

def setup_testcases():
    """Generate test cases for all supported languages"""
    
    # Technical and diverse test sentences
    test_sentences = [
        "The novel algorithm leverages a multi-head attention mechanism to process long-range dependencies in sequential data, outperforming previous models on benchmark datasets.",
        "Machine learning has revolutionized various industries by enabling computers to learn patterns from data without explicit programming.",
        "The implementation of blockchain technology ensures data integrity and transparency in distributed systems.",
        "Quantum computing promises to solve complex computational problems that are intractable for classical computers.",
        "Deep neural networks can automatically extract hierarchical features from raw input data through multiple layers of abstraction.",
        "The COVID-19 pandemic has accelerated digital transformation across healthcare, education, and business sectors.",
        "Climate change poses significant challenges to global food security and sustainable development goals.",
        "Artificial intelligence ethics requires careful consideration of bias, fairness, and accountability in algorithmic decision-making.",
        "The integration of IoT devices creates smart ecosystems that enhance efficiency and user experience in modern cities.",
        "Renewable energy technologies such as solar and wind power are becoming increasingly cost-effective alternatives to fossil fuels.",
        "Cybersecurity threats continue to evolve, requiring advanced detection and prevention mechanisms to protect sensitive information.",
        "Natural language processing enables computers to understand, interpret, and generate human language in meaningful ways.",
        "The development of autonomous vehicles involves complex sensor fusion, path planning, and real-time decision-making algorithms.",
        "Big data analytics helps organizations extract valuable insights from massive datasets to drive strategic business decisions.",
        "Virtual and augmented reality technologies are transforming entertainment, education, and professional training experiences."
    ]
    
    # Language-specific translations (human-quality references)
    translations = {
        "zh": [
            "该创新算法采用多头注意力机制处理序列数据中的长程依赖关系，在基准数据集上的表现优于以往模型。",
            "机器学习通过使计算机能够从数据中学习模式而无需显式编程，彻底改变了各个行业。",
            "区块链技术的实施确保了分布式系统中数据的完整性和透明度。",
            "量子计算有望解决对经典计算机来说难以处理的复杂计算问题。",
            "深度神经网络可以通过多层抽象自动从原始输入数据中提取分层特征。",
            "新冠疫情加速了医疗、教育和商业领域的数字化转型。",
            "气候变化对全球粮食安全和可持续发展目标构成重大挑战。",
            "人工智能伦理需要仔细考虑算法决策中的偏见、公平性和问责制。",
            "物联网设备的集成创造了智能生态系统，提高了现代城市的效率和用户体验。",
            "太阳能和风能等可再生能源技术正成为化石燃料日益经济有效的替代品。",
            "网络安全威胁持续演变，需要先进的检测和预防机制来保护敏感信息。",
            "自然语言处理使计算机能够以有意义的方式理解、解释和生成人类语言。",
            "自动驾驶汽车的开发涉及复杂的传感器融合、路径规划和实时决策算法。",
            "大数据分析帮助组织从海量数据集中提取有价值的洞察，以推动战略业务决策。",
            "虚拟现实和增强现实技术正在改变娱乐、教育和专业培训体验。"
        ],
        "es": [
            "El algoritmo novedoso aprovecha un mecanismo de atención multi-cabeza para procesar dependencias de largo alcance en datos secuenciales, superando a modelos anteriores en conjuntos de datos de referencia.",
            "El aprendizaje automático ha revolucionado varias industrias al permitir que las computadoras aprendan patrones de los datos sin programación explícita.",
            "La implementación de la tecnología blockchain asegura la integridad y transparencia de los datos en sistemas distribuidos.",
            "La computación cuántica promete resolver problemas computacionales complejos que son intratables para las computadoras clásicas.",
            "Las redes neuronales profundas pueden extraer automáticamente características jerárquicas de datos de entrada sin procesar a través de múltiples capas de abstracción.",
            "La pandemia de COVID-19 ha acelerado la transformación digital en los sectores de salud, educación y negocios.",
            "El cambio climático plantea desafíos significativos para la seguridad alimentaria global y los objetivos de desarrollo sostenible.",
            "La ética de la inteligencia artificial requiere una consideración cuidadosa del sesgo, la equidad y la responsabilidad en la toma de decisiones algorítmicas.",
            "La integración de dispositivos IoT crea ecosistemas inteligentes que mejoran la eficiencia y la experiencia del usuario en las ciudades modernas.",
            "Las tecnologías de energía renovable como la solar y eólica se están convirtiendo en alternativas cada vez más rentables a los combustibles fósiles.",
            "Las amenazas de ciberseguridad continúan evolucionando, requiriendo mecanismos avanzados de detección y prevención para proteger información sensible.",
            "El procesamiento de lenguaje natural permite a las computadoras entender, interpretar y generar lenguaje humano de maneras significativas.",
            "El desarrollo de vehículos autónomos involucra algoritmos complejos de fusión de sensores, planificación de rutas y toma de decisiones en tiempo real.",
            "El análisis de big data ayuda a las organizaciones a extraer insights valiosos de conjuntos de datos masivos para impulsar decisiones estratégicas de negocio.",
            "Las tecnologías de realidad virtual y aumentada están transformando las experiencias de entretenimiento, educación y entrenamiento profesional."
        ],
        "pt": [
            "O algoritmo inovador aproveita um mecanismo de atenção multi-cabeça para processar dependências de longo alcance em dados sequenciais, superando modelos anteriores em conjuntos de dados de referência.",
            "O aprendizado de máquina revolucionou várias indústrias ao permitir que computadores aprendam padrões dos dados sem programação explícita.",
            "A implementação da tecnologia blockchain garante a integridade e transparência dos dados em sistemas distribuídos.",
            "A computação quântica promete resolver problemas computacionais complexos que são intratáveis para computadores clássicos.",
            "Redes neurais profundas podem extrair automaticamente características hierárquicas de dados de entrada brutos através de múltiplas camadas de abstração.",
            "A pandemia de COVID-19 acelerou a transformação digital nos setores de saúde, educação e negócios.",
            "As mudanças climáticas representam desafios significativos para a segurança alimentar global e os objetivos de desenvolvimento sustentável.",
            "A ética da inteligência artificial requer consideração cuidadosa de viés, equidade e responsabilidade na tomada de decisões algorítmicas.",
            "A integração de dispositivos IoT cria ecossistemas inteligentes que melhoram a eficiência e a experiência do usuário em cidades modernas.",
            "Tecnologias de energia renovável como solar e eólica estão se tornando alternativas cada vez mais econômicas aos combustíveis fósseis.",
            "Ameaças de cibersegurança continuam a evoluir, exigindo mecanismos avançados de detecção e prevenção para proteger informações sensíveis.",
            "O processamento de linguagem natural permite que computadores entendam, interpretem e gerem linguagem humana de maneiras significativas.",
            "O desenvolvimento de veículos autônomos envolve algoritmos complexos de fusão de sensores, planejamento de rotas e tomada de decisões em tempo real.",
            "A análise de big data ajuda organizações a extrair insights valiosos de conjuntos de dados massivos para impulsionar decisões estratégicas de negócios.",
            "Tecnologias de realidade virtual e aumentada estão transformando experiências de entretenimento, educação e treinamento profissional."
        ],
        "ja": [
            "この新しいアルゴリズムは、マルチヘッドアテンション機構を活用してシーケンシャルデータの長距離依存関係を処理し、ベンチマークデータセットで従来のモデルを上回る性能を示している。",
            "機械学習は、明示的なプログラミングなしにコンピュータがデータからパターンを学習することを可能にし、様々な産業に革命をもたらした。",
            "ブロックチェーン技術の実装により、分散システムにおけるデータの整合性と透明性が確保される。",
            "量子コンピューティングは、従来のコンピュータでは処理困難な複雑な計算問題を解決することを約束している。",
            "深層ニューラルネットワークは、複数の抽象化層を通じて生の入力データから階層的特徴を自動的に抽出できる。",
            "COVID-19パンデミックは、医療、教育、ビジネス分野におけるデジタル変革を加速させた。",
            "気候変動は、世界の食料安全保障と持続可能な開発目標に重大な課題をもたらしている。",
            "人工知能の倫理は、アルゴリズムによる意思決定におけるバイアス、公平性、説明責任の慎重な検討を必要とする。",
            "IoTデバイスの統合により、現代都市の効率性とユーザー体験を向上させるスマートエコシステムが創造される。",
            "太陽光や風力などの再生可能エネルギー技術は、化石燃料に対してますます費用対効果の高い代替手段となっている。",
            "サイバーセキュリティの脅威は進化し続けており、機密情報を保護するための高度な検出・防止メカニズムが必要である。",
            "自然言語処理により、コンピュータは人間の言語を意味のある方法で理解、解釈、生成することができる。",
            "自動運転車の開発には、複雑なセンサー融合、経路計画、リアルタイム意思決定アルゴリズムが含まれる。",
            "ビッグデータ分析は、組織が大規模データセットから価値ある洞察を抽出し、戦略的ビジネス決定を推進するのに役立つ。",
            "バーチャルリアリティと拡張現実技術は、エンターテインメント、教育、専門訓練の体験を変革している。"
        ]
    }
    
    # Create test cases for each language
    languages = ["en", "zh", "es", "pt", "ja"]
    
    for lang in languages:
        test_dir = Path(f"testcases/{lang}")
        test_dir.mkdir(parents=True, exist_ok=True)
        
        test_file = test_dir / "test_suite.txt"
        
        print(f"Creating test cases for {lang}...")
        
        with open(test_file, 'w', encoding='utf-8') as f:
            if lang == "en":
                # English uses the original sentences
                for sentence in test_sentences:
                    f.write(sentence + '\n')
            else:
                # Other languages use their translations
                for sentence in translations[lang]:
                    f.write(sentence + '\n')
        
        print(f"✓ Created {len(test_sentences)} test cases in {test_file}")
    
    print(f"\n🎉 Test case setup complete!")
    print(f"Generated {len(test_sentences)} sentences for each of {len(languages)} languages")
    print("You can now run: python evaluation/eval.py --version v1")

if __name__ == "__main__":
    setup_testcases() 