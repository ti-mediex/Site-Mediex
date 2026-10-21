<?php
/**
 * COPIA SEM CREDENCIAIS de site/enviar-orcamento.php.
 *
 * O arquivo real esta no .gitignore porque guarda usuario e senha do SMTP
 * da Locaweb em texto puro. Para restaurar em um clone novo: copie este
 * arquivo para site/enviar-orcamento.php e preencha SMTP_USER_AQUI e
 * SMTP_SENHA_AQUI com as credenciais reais.
 *
 * Nao suba ESTE arquivo para o servidor: ele fica fora de site/ de proposito,
 * para o _ftp/upload.py nunca o enviar.
 */
/**
 * Endpoint de envio do orçamento de exames por e-mail (SMTP Locaweb).
 * Recebe o lead do formulário (JSON), valida e dispara e-mail para o comercial.
 *
 * Roda no servidor (cPanel) — as credenciais NÃO ficam expostas no navegador.
 * Servido só a partir do deploy; em ambiente de desenvolvimento (next dev) não executa.
 *
 * Segurança: mover as credenciais para variáveis de ambiente do cPanel quando possível
 * e rotacionar a senha do SMTP (foi compartilhada em texto puro).
 */

header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');

// ---- Configuração SMTP (Locaweb) ----
$SMTP = [
    'host' => 'smtplw.com.br',
    'port' => 587,            // 587 = STARTTLS. (A 465/SSL é recusada pela hospedagem: Connection refused 111.)
    'user' => 'SMTP_USER_AQUI',
    'pass' => 'SMTP_SENHA_AQUI',
    'from' => 'comercial@mediex.com.br',   // remetente (deve ser autorizado na conta Locaweb)
    'to'   => 'comercial@mediex.com.br',    // destino do lead
];

function respond($ok, $extra = []) {
    echo json_encode(array_merge(['ok' => $ok], $extra));
    exit;
}

// ---- Apenas POST ----
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    http_response_code(405);
    respond(false, ['error' => 'method_not_allowed']);
}

// ---- Lê o corpo (JSON ou form) ----
$raw = file_get_contents('php://input');
$data = json_decode($raw, true);
if (!is_array($data)) {
    $data = $_POST;
}

// ---- Honeypot anti-spam: se o campo oculto vier preenchido, é bot ----
if (!empty($data['website'])) {
    respond(true, ['skipped' => true]);
}

// ---- Sanitização ----
function clean($v) {
    return trim(preg_replace('/[\r\n]+/', ' ', (string)($v ?? '')));
}
$modalidade  = clean($data['modalidade'] ?? '');
$modalTitulo = clean($data['modalidadeTitulo'] ?? '');
$nome     = clean($data['nome'] ?? '');
$email    = clean($data['email'] ?? '');
$telefone = clean($data['telefone'] ?? '');
$cnpj     = clean($data['cnpj'] ?? '');
$empresa  = clean($data['empresa'] ?? '');
$cidade   = clean($data['cidade'] ?? '');
$colab    = clean($data['colaboradores'] ?? '');
// A landing nao envia mais estimativa de valor: a tabela de precos saiu do
// ExamLeadForm em 2026-08-05 (ia inteira para o bundle JS publico). O e-mail do
// comercial deixou de trazer as linhas de estimativa junto.
$criado   = clean($data['criadoEm'] ?? '');
$origem   = clean($data['origem'] ?? '');
$pagina   = clean($data['pagina'] ?? '');

$servicos = $data['servicos'] ?? [];
if (!is_array($servicos)) $servicos = [];
$servicos = array_map('clean', $servicos);

// Só o formulário da landing de exames (ExamLeadForm, origem "landing-exames")
// exige e-mail e traz exames/modalidade. Os demais leads (pop de captura,
// orçamento de artigo do blog) são simplificados: validados pelo WhatsApp e
// com um e-mail próprio, mais enxuto.
$isExames = strpos($origem, 'landing-exames') === 0;

$exames = $data['exames'] ?? [];
if (!is_array($exames)) $exames = [];
$exames = array_map('clean', $exames);

// ---- Validação mínima ----
if ($isExames) {
    if ($email === '' || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
        http_response_code(422);
        respond(false, ['error' => 'email_invalido']);
    }
} elseif ($telefone === '' && $email === '') {
    // Leads simplificados (pop, orçamento de blog): o contato é o WhatsApp.
    http_response_code(422);
    respond(false, ['error' => 'contato_ausente']);
}

// ---- Monta o corpo do e-mail ----

// Todos os leads vão para o comercial.
$SMTP['to'] = 'comercial@mediex.com.br';

if (!$isExames) {
    // Lead simplificado: pop de captura ou orçamento de artigo do blog.
    $quem = $empresa !== '' ? $empresa : ($nome !== '' ? $nome : 'lead do site');

    // Rótulo amigável no assunto conforme a origem.
    $rotulo = 'Novo lead';
    if (strpos($origem, 'leadpop') === 0) {
        $rotulo = 'Novo lead — Condição especial';
    } elseif (strpos($origem, 'blog-orcamento') === 0) {
        $rotulo = 'Novo orçamento (artigo do blog)';
    }
    $assunto = $rotulo . ' — ' . $quem;

    $corpo  = "Novo lead capturado no site.\n\n";
    $corpo .= "Nome: " . ($nome !== '' ? $nome : '-') . "\n";
    $corpo .= "Empresa: " . ($empresa !== '' ? $empresa : '-') . "\n";
    $corpo .= "CNPJ: " . ($cnpj !== '' ? $cnpj : '-') . "\n";
    $corpo .= "Cidade: " . ($cidade !== '' ? $cidade : '-') . "\n";
    $corpo .= "WhatsApp: " . ($telefone !== '' ? $telefone : '-') . "\n";
    if ($email !== '') $corpo .= "E-mail: " . $email . "\n";
    if ($colab !== '' && $colab !== '0') $corpo .= "Nº de colaboradores: " . $colab . "\n";
    if (!empty($servicos)) $corpo .= "Serviços de interesse: " . implode(', ', $servicos) . "\n";
    $corpo .= "Origem: " . ($origem !== '' ? $origem : '-') . "\n";
    $corpo .= "Página: " . ($pagina !== '' ? $pagina : '-') . "\n";
    $corpo .= "Recebido em: " . ($criado !== '' ? $criado : date('c')) . "\n";
} else {
    $listaExames = $exames ? "\n - " . implode("\n - ", $exames) : ' (nenhum selecionado)';
    $labelModal = $modalTitulo !== '' ? $modalTitulo : ($modalidade !== '' ? $modalidade : '-');
    $quem = $empresa !== '' ? $empresa : ($cnpj !== '' ? $cnpj : 'lead do site');
    $assunto = 'Novo orçamento de exames (' . $labelModal . ') — ' . $quem;

    $corpo  = "Novo orçamento gerado na landing de exames.\n\n";
    $corpo .= "Forma de atendimento: " . $labelModal . "\n";
    $corpo .= "Empresa: " . ($empresa !== '' ? $empresa : '-') . "\n";
    $corpo .= "CNPJ: " . ($cnpj !== '' ? $cnpj : '-') . "\n";
    $corpo .= "Cidade: " . ($cidade !== '' ? $cidade : '-') . "\n";
    $corpo .= "Responsável: " . ($nome !== '' ? $nome : '-') . "\n";
    $corpo .= "E-mail: " . $email . "\n";
    $corpo .= "Telefone/WhatsApp: " . ($telefone !== '' ? $telefone : '-') . "\n";
    $corpo .= "Nº de colaboradores: " . ($colab !== '' ? $colab : '-') . "\n\n";
    $corpo .= "Exames selecionados:" . $listaExames . "\n\n";
    $corpo .= "(Sem estimativa de valor: a precificacao e feita pelo comercial conforme os riscos e o PCMSO da empresa.)\n\n";
    $corpo .= "Gerado em: " . ($criado !== '' ? $criado : date('c')) . "\n";
}

// ---- Envia via SMTP; se recusar, fallback para o mail() do servidor (MTA local) ----
$erro = smtp_send($SMTP, $assunto, $corpo, $email, $nome);
if ($erro === '') {
    respond(true, ['via' => 'smtp']);
}

// Fallback: função mail() local — usada enquanto o dominio nao esta liberado no SMTP Locaweb.
$replyEmail = ($email !== '' && filter_var($email, FILTER_VALIDATE_EMAIL)) ? $email : $SMTP['from'];
$subjEnc = '=?UTF-8?B?' . base64_encode($assunto) . '?=';
$mailHeaders = implode("\r\n", [
    'From: Mediex Site <' . $SMTP['from'] . '>',
    'Reply-To: ' . ($nome !== '' ? "{$nome} <{$replyEmail}>" : $replyEmail),
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 8bit',
]);
$corpoMail = str_replace(["\r\n", "\r"], "\n", $corpo);
$okMail = @mail($SMTP['to'], $subjEnc, $corpoMail, $mailHeaders, '-f' . $SMTP['from']);
if ($okMail) {
    respond(true, ['via' => 'mail_local']);
}
http_response_code(502);
respond(false, ['error' => 'smtp_e_mail', 'detail' => $erro]);

// ============================================================
// Cliente SMTP mínimo (AUTH LOGIN, SSL 465 ou STARTTLS 587)
// ============================================================
function smtp_send($cfg, $assunto, $corpo, $replyEmail = '', $replyNome = '') {
    $host = $cfg['host'];
    $port = (int)$cfg['port'];
    $from = $cfg['from'];
    $to   = $cfg['to'];

    $transport = ($port === 465) ? "ssl://{$host}:{$port}" : "tcp://{$host}:{$port}";
    $ctx = stream_context_create(['ssl' => [
        'verify_peer' => true,
        'verify_peer_name' => true,
        'SNI_enabled' => true,
    ]]);

    $errno = 0; $errstr = '';
    $fp = @stream_socket_client($transport, $errno, $errstr, 20, STREAM_CLIENT_CONNECT, $ctx);
    if (!$fp) return "conexao_falhou: {$errstr} ({$errno})";
    stream_set_timeout($fp, 20);

    $read = function () use ($fp) {
        $out = '';
        while (($line = fgets($fp, 515)) !== false) {
            $out .= $line;
            if (strlen($line) >= 4 && $line[3] === ' ') break; // fim do multiline
        }
        return $out;
    };
    $send = function ($cmd) use ($fp) { fwrite($fp, $cmd . "\r\n"); };
    $code = function ($resp) { return substr($resp, 0, 3); };

    if ($code($read()) !== '220') { fclose($fp); return 'sem_greeting'; }

    $send("EHLO mediex.com.br");
    $ehlo = $read();
    if ($code($ehlo) !== '250') {
        $send("HELO mediex.com.br");
        if ($code($read()) !== '250') { fclose($fp); return "ehlo_falhou: {$ehlo}"; }
    }

    // STARTTLS na porta 587
    if ($port === 587) {
        $send("STARTTLS");
        if ($code($read()) !== '220') { fclose($fp); return 'starttls_negado'; }
        if (!stream_socket_enable_crypto($fp, true, STREAM_CRYPTO_METHOD_TLS_CLIENT)) {
            fclose($fp); return 'tls_handshake_falhou';
        }
        $send("EHLO mediex.com.br");
        if ($code($read()) !== '250') { fclose($fp); return 'ehlo2_falhou'; }
    }

    $send("AUTH LOGIN");
    if ($code($read()) !== '334') { fclose($fp); return 'auth_login_negado'; }
    $send(base64_encode($cfg['user']));
    if ($code($read()) !== '334') { fclose($fp); return 'usuario_negado'; }
    $send(base64_encode($cfg['pass']));
    if ($code($read()) !== '235') { fclose($fp); return 'senha_rejeitada'; }

    $send("MAIL FROM:<{$from}>");
    if ($code($read()) !== '250') { fclose($fp); return 'mail_from_negado'; }
    $send("RCPT TO:<{$to}>");
    $rcpt = $code($read());
    if ($rcpt !== '250' && $rcpt !== '251') { fclose($fp); return 'rcpt_negado'; }
    $send("DATA");
    if ($code($read()) !== '354') { fclose($fp); return 'data_negado'; }

    $subjEnc = '=?UTF-8?B?' . base64_encode($assunto) . '?=';
    $replyTo = ($replyEmail !== '' && filter_var($replyEmail, FILTER_VALIDATE_EMAIL))
        ? ($replyNome !== '' ? "{$replyNome} <{$replyEmail}>" : $replyEmail)
        : '';

    $headers  = "From: Mediex Site <{$from}>\r\n";
    $headers .= "To: <{$to}>\r\n";
    if ($replyTo !== '') $headers .= "Reply-To: {$replyTo}\r\n";
    $headers .= "Subject: {$subjEnc}\r\n";
    $headers .= "MIME-Version: 1.0\r\n";
    $headers .= "Content-Type: text/plain; charset=UTF-8\r\n";
    $headers .= "Content-Transfer-Encoding: 8bit\r\n";
    $headers .= "Date: " . date('r') . "\r\n";

    // Normaliza quebras e faz dot-stuffing (linhas iniciadas por ".")
    $body = str_replace("\n", "\r\n", str_replace(["\r\n", "\r"], "\n", $corpo));
    $body = preg_replace('/^\./m', '..', $body);

    fwrite($fp, $headers . "\r\n" . $body . "\r\n.\r\n");
    $finalResp = $read();
    if ($code($finalResp) !== '250') { fclose($fp); return 'envio_recusado: ' . trim($finalResp); }

    $send("QUIT");
    fclose($fp);
    return '';
}
